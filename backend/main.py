"""backend/main.py
FastAPI entrypoint for Grant Reviewer backend.
"""

import hashlib
import hmac
import json
import logging
import os
import time
from collections.abc import Generator
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Annotated, Any, Literal
from uuid import UUID

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Query, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.db import create_db_and_tables, get_session, ping_database
from app.models.domain import ProposalSnippet, ReviewRating, ReviewStatus
from app.repositories.review_repository import ReviewRepository
from app.schemas.api import (
    APIErrorBody,
    APIErrorResponse,
    CallConfigResponse,
    CallsResponse,
    CallSummary,
    CreateReviewRequest,
    CreateReviewResponse,
    DeleteReviewResponse,
    DomainOptionDTO,
    NodeMetadataResponse,
    NodesResponse,
    NodesTreeResponse,
    NodeSummary,
    NodeTreeNode,
    ReviewCardSummary,
    ReviewCompatibilityNote,
    ReviewDetailResponse,
    ReviewDetailProjection,
    ReviewListItem,
    ReviewsListResponse,
    ReviewSummary,
    SupportTraceMetadata,
)
from app.schemas.compliance import ComplianceCheckRequest, ComplianceCheckResponse
from app.schemas.structured_review import (
    MAX_NODE_TEXT_CHARS,
    MAX_STRUCTURED_PAYLOAD_CHARS,
    StructuredReviewRequest,
)
from app.services.call_definition_service import CallDefinitionService
from app.services.compliance_engine import (
    evaluate_compliance,
    find_supporting_node_ids_in_primary_path_draft,
)
from app.services.llm_client import build_llm_client
from app.services.node_metadata_service import NodeMetadataService
from app.services.node_tree_service import (
    NodeTreeCycleError,
    NodeTreeMismatchError,
    NodeTreeService,
)
from app.services.reviewer_policy import matches_review_stage
from app.services.reviewer_service import ReviewerService
from app.services.structured_reviewer_service import (
    StructuredReviewerService,
    resolve_supporting_node_logical_ids_for_primary_path,
)

logger = logging.getLogger(__name__)

# Local developer convenience: load `backend/.env` when present.
# In prod, prefer injecting env vars via the deployment environment.
_BACKEND_ENV_PATH = Path(__file__).resolve().parent / ".env"
if _BACKEND_ENV_PATH.is_file():
    load_dotenv(dotenv_path=_BACKEND_ENV_PATH, override=False)

MAX_SNIPPET_CHARS = 10_000
BFF_SIGNATURE_MAX_AGE_SECONDS = 300
IDEMPOTENCY_TTL_HOURS = 24
FREE_DAILY_REVIEW_LIMIT = 5
FREE_DAILY_REVIEW_LIMIT_DEV_DEFAULT = 10_000
WF0080_SUPPORT_TRACE_HEADER = "X-GR-Support-Trace"
WF0080_LAUNCH_WEDGE_CALL_CODE = "ERC-2026-PoC"


def is_idempotency_conflict_error(err: IntegrityError) -> bool:
    error_text = str(err.orig).lower() if err.orig is not None else str(err).lower()
    return (
        "uq_review_external_idempotency" in error_text
        or "unique constraint failed: reviews.external_user_id, reviews.idempotency_key"
        in error_text
        or (
            "duplicate key value violates unique constraint" in error_text
            and "idempotency" in error_text
        )
    )

ERROR_STATUS_BY_CODE = {
    "UNAUTHORIZED": 401,
    "COHORT_ACCESS_DENIED": 403,
    "IDEMPOTENCY_PAYLOAD_MISMATCH": 409,
    "QUOTA_EXCEEDED": 429,
    "CALL_NOT_FOUND": 404,
    "NODE_NOT_FOUND": 404,
    "REVIEW_NOT_FOUND": 404,
    "NO_EXPECTATIONS": 400,
    "NODE_NOT_IN_CALL": 400,
    "REVIEW_STAGE_NODE_MISMATCH": 422,
    "REVIEWS_DISABLED": 503,
    "DB_UNAVAILABLE": 503,
    "SNIPPET_TOO_LONG": 400,
    "UNKNOWN_NODE_ID": 422,
    "DUPLICATE_NODE_ID": 422,
    "SUPPORTING_NODE_NOT_ALLOWED": 422,
    "DOMAIN_REQUIRED": 422,
    "DOMAIN_INVALID": 422,
    "STRUCTURED_NODES_REQUIRED": 422,
    "STRUCTURED_PAYLOAD_TOO_LARGE": 422,
    "CALL_DEFINITION_NODE_MISMATCH": 409,
    "CALL_DEFINITION_CYCLE": 409,
    "CALL_DEFINITION_MISSING": 409,
    "VALIDATION_ERROR": 400,
    "INTERNAL_ERROR": 500,
}

API_ERROR_RESPONSES = {
    401: {"model": APIErrorResponse},
    403: {"model": APIErrorResponse},
    409: {"model": APIErrorResponse},
    429: {"model": APIErrorResponse},
    400: {"model": APIErrorResponse},
    422: {"model": APIErrorResponse},
    404: {"model": APIErrorResponse},
    500: {"model": APIErrorResponse},
    503: {"model": APIErrorResponse},
}

NODE_LOGICAL_IDS_QUERY = Query(default=None)


class APIException(Exception):
    """API-level error with canonical code/message/details."""

    def __init__(
        self,
        *,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        self.headers = headers or {}
        super().__init__(message)


@asynccontextmanager
async def app_lifespan(_: FastAPI):
    """Initialize DB tables on startup."""
    create_db_and_tables()
    yield


app = FastAPI(
    title="Grant Reviewer API",
    version="0.1.0",
    lifespan=app_lifespan,
)


def build_error_response(
    *,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    """Build canonical error JSON response."""
    payload = APIErrorResponse(
        error=APIErrorBody(code=code, message=message, details=details or {}),
    )
    status_code = ERROR_STATUS_BY_CODE.get(code, 500)
    return JSONResponse(
        status_code=status_code,
        content=payload.model_dump(mode="json"),
        headers=headers,
    )


@app.exception_handler(APIException)
async def api_exception_handler(_: Request, exc: APIException) -> JSONResponse:
    """Handle known API exceptions."""
    return build_error_response(
        code=exc.code,
        message=exc.message,
        details=exc.details,
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Handle request schema validation failures."""
    return build_error_response(
        code="VALIDATION_ERROR",
        message="Request payload validation failed.",
        details={"errors": exc.errors()},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected server failures."""
    logger.exception("Unhandled API error: %s", exc)
    return build_error_response(
        code="INTERNAL_ERROR",
        message="Unexpected server error.",
    )


def get_repository() -> Generator[ReviewRepository, None, None]:
    """Dependency: create request-scoped repository."""
    session = get_session()
    try:
        yield ReviewRepository(session)
    finally:
        session.close()


def _build_signature_payload(*, user_id: str, timestamp: int, body: bytes) -> str:
    """Build canonical string signed by BFF."""
    body_hash = hashlib.sha256(body).hexdigest()
    return f"{user_id}.{timestamp}.{body_hash}"


def _is_reviews_enabled() -> bool:
    """Parse REVIEWS_ENABLED env var as bool with safe default."""
    raw = os.getenv("REVIEWS_ENABLED", "true").strip().lower()
    return raw not in {"0", "false", "no", "off"}


def _get_free_daily_review_limit() -> int:
    """Read per-user daily review limit from env."""
    raw_limit = os.getenv("FREE_DAILY_REVIEW_LIMIT")
    if raw_limit is None:
        app_env = os.getenv("APP_ENV", "").strip().lower()
        if app_env in {"dev", "development", "local"}:
            return FREE_DAILY_REVIEW_LIMIT_DEV_DEFAULT
        return FREE_DAILY_REVIEW_LIMIT

    raw = raw_limit.strip()
    try:
        return max(0, int(raw))
    except ValueError:
        logger.warning(
            "Invalid FREE_DAILY_REVIEW_LIMIT=%s; falling back to default", raw
        )
        app_env = os.getenv("APP_ENV", "").strip().lower()
        if app_env in {"dev", "development", "local"}:
            return FREE_DAILY_REVIEW_LIMIT_DEV_DEFAULT
        return FREE_DAILY_REVIEW_LIMIT


def _is_wf0080_launch_wedge_call(call_code: str | None) -> bool:
    """Return whether the call is inside the approved WF-0080 launch wedge."""
    return call_code == WF0080_LAUNCH_WEDGE_CALL_CODE


def _build_wf0080_support_trace_id(
    *,
    call_code: str | None,
    external_user_id: str | None,
    idempotency_key: str | None,
) -> str | None:
    """Build a deterministic support trace from existing request/review identifiers."""
    if not call_code or not external_user_id or not idempotency_key:
        return None

    trace_material = "::".join((call_code, external_user_id, idempotency_key))
    digest = hashlib.sha256(trace_material.encode("utf-8")).hexdigest()[:20]
    return f"wf0080-{digest}"


def _build_wf0080_support_trace_metadata(
    *,
    call_code: str | None,
    external_user_id: str | None,
    idempotency_key: str | None,
) -> SupportTraceMetadata | None:
    """Build bounded WF-0080 support metadata without widening storage."""
    if not _is_wf0080_launch_wedge_call(call_code):
        return None

    trace_id = _build_wf0080_support_trace_id(
        call_code=call_code,
        external_user_id=external_user_id,
        idempotency_key=idempotency_key,
    )
    if trace_id is None:
        return None

    return SupportTraceMetadata(
        contract="wf0080_support_trace_v1",
        trace_id=trace_id,
        visibility="maintainer_support_only",
    )


def _set_support_trace_header(
    response: Response,
    support_trace: SupportTraceMetadata | None,
) -> None:
    """Expose the bounded support trace on response headers when available."""
    if support_trace is None:
        return
    response.headers[WF0080_SUPPORT_TRACE_HEADER] = support_trace.trace_id


async def require_bff_user_id(request: Request) -> str:
    """Validate BFF signature headers and return external user id."""
    user_id = request.headers.get("X-GR-User-Id")
    timestamp_raw = request.headers.get("X-GR-Timestamp")
    signature = request.headers.get("X-GR-Signature")
    if not user_id or not timestamp_raw or not signature:
        raise APIException(
            code="UNAUTHORIZED",
            message="Missing authentication signature headers.",
        )

    try:
        timestamp = int(timestamp_raw)
    except ValueError as err:
        raise APIException(
            code="UNAUTHORIZED",
            message="Invalid authentication timestamp.",
        ) from err

    now = int(time.time())
    if abs(now - timestamp) > BFF_SIGNATURE_MAX_AGE_SECONDS:
        raise APIException(
            code="UNAUTHORIZED",
            message="Authentication signature has expired.",
        )

    shared_secret = os.getenv("BFF_SHARED_SECRET")
    if not shared_secret:
        raise APIException(
            code="UNAUTHORIZED",
            message="Authentication signature verification failed.",
        )

    body = await request.body()
    payload = _build_signature_payload(user_id=user_id, timestamp=timestamp, body=body)
    expected_signature = hmac.new(
        shared_secret.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(expected_signature, signature):
        raise APIException(
            code="UNAUTHORIZED",
            message="Authentication signature verification failed.",
        )

    return user_id


def map_review_failure_to_api_error(error: ValueError) -> APIException:
    """Translate service errors to canonical API errors."""
    message = str(error)
    if message == "No evaluation criteria defined for this section.":
        return APIException(code="NO_EXPECTATIONS", message=message)
    return APIException(code="INTERNAL_ERROR", message="Review generation failed.")


def _normalize_domain(domain: str | None) -> str | None:
    """Normalize domain string to canonical lowercase identifier."""
    if domain is None:
        return None
    normalized = domain.strip().lower()
    return normalized or None


def _is_domain_limited_node(node_config: dict[str, Any]) -> bool:
    """Return True when node has domain-specific word limit configuration."""
    constraints = node_config.get("content_constraints")
    if not isinstance(constraints, dict):
        return False
    by_domain = constraints.get("word_limit_by_domain")
    return isinstance(by_domain, dict)


def _has_domain_default_fallback(node_config: dict[str, Any]) -> bool:
    """Return True if node has usable default_max_words fallback."""
    constraints = node_config.get("content_constraints")
    if not isinstance(constraints, dict):
        return False
    by_domain = constraints.get("word_limit_by_domain")
    if not isinstance(by_domain, dict):
        return False
    return isinstance(by_domain.get("default_max_words"), int)


def _resolve_review_call_id(review: Any, repository: ReviewRepository) -> UUID | None:
    """Resolve call id for single or structured review records."""
    if review.proposal_snippet_id is not None:
        snippet = repository.session.get(ProposalSnippet, review.proposal_snippet_id)
        if snippet is not None:
            return snippet.funding_call_id

    structured_payload = review.structured_payload
    if isinstance(structured_payload, dict):
        payload_call_id = structured_payload.get("call_id")
        if isinstance(payload_call_id, str):
            try:
                return UUID(payload_call_id)
            except ValueError:
                return None

    return None


def _infer_review_detail_state(
    *,
    call_id: UUID | None,
    call_code: str | None,
    ordering_source: Literal["call_nodes", "review_payload_fallback"],
    unmapped_node_logical_ids: list[str],
) -> Literal["call_linked", "legacy_fallback", "proof_path_unmapped"]:
    if ordering_source == "review_payload_fallback" or call_id is None:
        return "legacy_fallback"
    if call_code == "erc_stg_2026_full" and unmapped_node_logical_ids:
        return "proof_path_unmapped"
    return "call_linked"


def _partition_visible_by_stage_scope(
    *,
    visible_not_reviewed: list[str],
    structured_payload: dict[str, Any] | None,
) -> tuple[list[str], list[str]]:
    """Split visible-not-reviewed nodes into in-scope and out-of-scope buckets.

    Returns (visible_not_reviewed, out_of_scope).  When no persisted
    ``stage_scope_leaf_ids`` exists (legacy reviews), returns the original
    list unchanged with an empty out-of-scope bucket.
    """
    payload = structured_payload if isinstance(structured_payload, dict) else {}
    persisted_scope = payload.get("stage_scope_leaf_ids")
    if not isinstance(persisted_scope, list) or not persisted_scope:
        return visible_not_reviewed, []

    scope_set = {s for s in persisted_scope if isinstance(s, str) and s.strip()}
    out_of_scope = sorted(
        node_id for node_id in visible_not_reviewed if node_id not in scope_set
    )
    remaining = sorted(
        node_id for node_id in visible_not_reviewed if node_id in scope_set
    )
    return remaining, out_of_scope


def _build_call_order_index_map(
    call_id: UUID,
    repository: ReviewRepository,
) -> dict[str, int | None]:
    """Build logical-id to order-index map from call definition or persisted nodes."""
    definition = repository.get_call_definition_by_call_id(call_id)
    order_map: dict[str, int | None] = {}
    if definition is not None and isinstance(definition.canonical_json, dict):
        proposal_nodes = definition.canonical_json.get("proposal_nodes")
        if isinstance(proposal_nodes, list):
            for position, node in enumerate(proposal_nodes):
                if not isinstance(node, dict):
                    continue
                logical_id = node.get("id")
                if not isinstance(logical_id, str) or not logical_id.strip():
                    continue
                raw_order_index = node.get("order_index")
                order_map[logical_id] = (
                    raw_order_index if isinstance(raw_order_index, int) else position
                )
    if order_map:
        return order_map

    for node, _ in repository.get_nodes_for_call(call_id):
        if isinstance(node.logical_id, str):
            order_map[node.logical_id] = node.order_index
    return order_map


def _extract_source_hints_by_logical_id(
    canonical_json: dict[str, Any],
) -> tuple[dict[str, str], dict[str, str]]:
    """Build criterion/element source-hint lookups from call definition metadata."""
    criterion_hints: dict[str, str] = {}
    element_hints: dict[str, str] = {}
    raw_criteria = canonical_json.get("evaluation_criteria")
    if not isinstance(raw_criteria, list):
        return criterion_hints, element_hints

    for raw_criterion in raw_criteria:
        if not isinstance(raw_criterion, dict):
            continue
        criterion_logical_id = raw_criterion.get("id")
        criterion_source_hint = raw_criterion.get("source_hint")
        if isinstance(criterion_logical_id, str) and isinstance(criterion_source_hint, str):
            stripped_hint = criterion_source_hint.strip()
            if stripped_hint:
                criterion_hints[criterion_logical_id] = stripped_hint

        raw_elements = raw_criterion.get("evaluation_elements")
        if not isinstance(raw_elements, list):
            continue
        for raw_element in raw_elements:
            if not isinstance(raw_element, dict):
                continue
            element_logical_id = raw_element.get("id")
            element_source_hint = raw_element.get("source_hint")
            if not isinstance(element_logical_id, str) or not isinstance(
                element_source_hint, str
            ):
                continue
            stripped_hint = element_source_hint.strip()
            if stripped_hint:
                element_hints[element_logical_id] = stripped_hint

    return criterion_hints, element_hints


def _resolve_card_source_basis(
    *,
    has_call_linkage: bool,
    criterion_logical_id: str | None,
    element_logical_id: str | None,
    criterion_hints: dict[str, str],
    element_hints: dict[str, str],
) -> tuple[str | None, Literal["available", "unavailable", "legacy_fallback"]]:
    """Resolve per-card source-basis fields with fail-closed precedence."""
    if not has_call_linkage:
        return None, "legacy_fallback"

    if isinstance(element_logical_id, str):
        element_hint = element_hints.get(element_logical_id)
        if isinstance(element_hint, str) and element_hint.strip():
            return element_hint, "available"
    if isinstance(criterion_logical_id, str):
        criterion_hint = criterion_hints.get(criterion_logical_id)
        if isinstance(criterion_hint, str) and criterion_hint.strip():
            return criterion_hint, "available"
    return None, "unavailable"


def _order_review_cards(
    cards: list[ReviewCardSummary],
    *,
    order_map: dict[str, int | None],
) -> tuple[list[ReviewCardSummary], list[str]]:
    """Sort cards deterministically and report unmapped logical ids."""
    unmapped = sorted(
        {
            card.node_logical_id
            for card in cards
            if isinstance(card.node_logical_id, str)
            and card.node_logical_id not in order_map
        }
    )

    def sort_key(card: ReviewCardSummary) -> tuple[int, int, str]:
        logical_id = card.node_logical_id if isinstance(card.node_logical_id, str) else ""
        order_index = order_map.get(logical_id)
        is_unmapped = logical_id == "" or logical_id not in order_map
        normalized_order = order_index if isinstance(order_index, int) else 1_000_000_000
        return (1 if is_unmapped else 0, normalized_order, logical_id)

    return sorted(cards, key=sort_key), unmapped


def _build_wf0080_detail_projection(
    cards: list[ReviewCardSummary],
) -> ReviewDetailProjection:
    """Build the bounded launch-wedge projection from existing card truth."""
    rating_priority = {
        ReviewRating.CRITICAL: 0,
        ReviewRating.WARNING: 1,
        ReviewRating.NOTE: 2,
        ReviewRating.SUCCESS: 3,
    }
    ranked_cards = sorted(
        enumerate(cards),
        key=lambda item: (
            0 if item[1].assessment_status == "NOT_ASSESSABLE" else 1,
            rating_priority.get(item[1].rating, 99),
            item[0],
        ),
    )
    ordered_card_ids = [card.id for _, card in ranked_cards]
    no_critical_blockers = bool(cards) and all(
        card.assessment_status == "ASSESSED"
        and card.rating in {ReviewRating.NOTE, ReviewRating.SUCCESS}
        for card in cards
    )
    return ReviewDetailProjection(
        version="wf0080_launch_wedge_v1",
        headline_state=(
            "no_critical_blockers" if no_critical_blockers else "action_required"
        ),
        ordered_card_ids=ordered_card_ids,
        top_action_card_ids=ordered_card_ids[:3],
        ranking_basis="assessment_status_then_rating_then_existing_order",
    )


def _extract_known_domains(node_config: dict[str, Any]) -> set[str]:
    """Extract canonical domain ids from word_limit_by_domain keys."""
    constraints = node_config.get("content_constraints")
    if not isinstance(constraints, dict):
        return set()
    by_domain = constraints.get("word_limit_by_domain")
    if not isinstance(by_domain, dict):
        return set()

    domains: set[str] = set()
    for key in by_domain:
        if not isinstance(key, str):
            continue
        if key == "default_max_words":
            continue
        if key.endswith("_max_words"):
            domains.add(key[: -len("_max_words")])
    return domains


def _to_domain_label(domain_id: str) -> str:
    """Convert canonical domain ids to a human-readable fallback label."""
    return domain_id.replace("_", " ").strip().title()


def _extract_domain_options(canonical_json: dict[str, Any]) -> list[DomainOptionDTO]:
    """Extract deterministic domain options from call definition metadata."""
    value_to_rank: dict[str, int] = {}
    value_to_label: dict[str, str] = {}

    funding_call = canonical_json.get("funding_call")
    if isinstance(funding_call, dict):
        domain_notes = funding_call.get("domain_notes")
        if isinstance(domain_notes, list):
            for index, note in enumerate(domain_notes):
                if not isinstance(note, dict):
                    continue
                domain_id = note.get("domain_id")
                if not isinstance(domain_id, str) or not domain_id.strip():
                    continue
                value = domain_id.strip().lower()
                value_to_rank.setdefault(value, index)
                raw_label = note.get("label")
                if isinstance(raw_label, str) and raw_label.strip():
                    value_to_label.setdefault(value, raw_label.strip())

    proposal_nodes = canonical_json.get("proposal_nodes")
    if isinstance(proposal_nodes, list):
        for node in proposal_nodes:
            if not isinstance(node, dict):
                continue
            for domain in _extract_known_domains(node):
                value_to_rank.setdefault(domain, 1_000_000_000)
                value_to_label.setdefault(domain, _to_domain_label(domain))

    sorted_values = sorted(value_to_rank.keys(), key=lambda value: (value_to_rank[value], value))
    return [
        DomainOptionDTO(
            value=value,
            label=value_to_label.get(value, _to_domain_label(value)),
            order_index=index,
        )
        for index, value in enumerate(sorted_values)
    ]


def _is_split_visibility_reviewability_enabled(canonical_json: dict[str, Any]) -> bool:
    runtime_config = canonical_json.get("runtime_config")
    if not isinstance(runtime_config, dict):
        return False
    return runtime_config.get("split_visibility_reviewability_enabled") is True


def _extract_node_roles_by_logical_id(
    *,
    canonical_json: dict[str, Any],
    split_opt_in_enabled: bool,
) -> dict[str, Literal["PRIMARY", "SUPPORTING"]]:
    if not split_opt_in_enabled:
        return {}

    proposal_nodes = canonical_json.get("proposal_nodes")
    if not isinstance(proposal_nodes, list):
        return {}

    node_roles: dict[str, Literal["PRIMARY", "SUPPORTING"]] = {}
    for node in proposal_nodes:
        if not isinstance(node, dict):
            continue
        logical_id = node.get("id")
        if not isinstance(logical_id, str) or not logical_id.strip():
            continue
        node_role = node.get("node_role")
        if node_role in {"PRIMARY", "SUPPORTING"}:
            node_roles[logical_id] = node_role
        else:
            node_roles[logical_id] = "PRIMARY"
    return node_roles


RepositoryDep = Annotated[ReviewRepository, Depends(get_repository)]


@app.get("/health")
def health() -> dict[str, bool]:
    """Liveness endpoint."""
    return {"ok": True}


@app.get("/health/db")
def health_db() -> dict[str, bool]:
    """Readiness endpoint: DB must be reachable."""
    try:
        ping_database()
    except Exception as exc:
        logger.warning("Database readiness check failed: %s", exc)
        raise APIException(
            code="DB_UNAVAILABLE",
            message="Database is unavailable.",
        ) from exc
    return {"ok": True}


@app.get("/calls", response_model=CallsResponse, responses=API_ERROR_RESPONSES)
def list_calls(repository: RepositoryDep) -> CallsResponse:
    """List active funding calls."""
    calls = repository.get_active_calls()
    return CallsResponse(
        calls=[
            CallSummary(
                id=call.id,
                code=call.code,
                name=call.name,
                year=call.call_year,
                agency_short_name=agency.short_name,
            )
            for call, agency in calls
        ],
    )


@app.get(
    "/api/public/calls/{call_logical_id}/config",
    response_model=CallConfigResponse,
    response_model_exclude_none=True,
    responses=API_ERROR_RESPONSES,
)
def get_call_config(call_logical_id: str, repository: RepositoryDep) -> CallConfigResponse:
    """Return public call config used by frontend mode gating."""
    call = repository.get_active_call_by_code(call_logical_id)
    if call is None:
        raise APIException(code="CALL_NOT_FOUND", message="Funding call not found.")

    definition = repository.get_call_definition_by_call_id(call.id)
    if definition is None:
        return CallConfigResponse(
            call_logical_id=call_logical_id,
            config_version="1",
            ui_mode="legacy_single_snippet",
            domain_options=[],
            split_visibility_reviewability_enabled=False,
        )

    canonical_json = definition.canonical_json
    split_opt_in_enabled = _is_split_visibility_reviewability_enabled(canonical_json)
    proposal_nodes = canonical_json.get("proposal_nodes")
    if not isinstance(proposal_nodes, list):
        logger.warning(
            "Call config fallback to legacy for %s: canonical_json.proposal_nodes is not a list",
            call_logical_id,
        )
        return CallConfigResponse(
            call_logical_id=call_logical_id,
            config_version="1",
            ui_mode="legacy_single_snippet",
            domain_options=[],
            split_visibility_reviewability_enabled=split_opt_in_enabled,
        )

    expected_nodes = [
        node_id
        for item in proposal_nodes
        if isinstance(item, dict)
        for node_id in [item.get("id")]
        if isinstance(node_id, str) and node_id.strip()
    ]
    if not expected_nodes:
        logger.warning(
            "Call config fallback to legacy for %s: no valid proposal node ids in canonical_json.proposal_nodes",
            call_logical_id,
        )
        return CallConfigResponse(
            call_logical_id=call_logical_id,
            config_version="1",
            ui_mode="legacy_single_snippet",
            domain_options=[],
            split_visibility_reviewability_enabled=split_opt_in_enabled,
        )

    domain_options = _extract_domain_options(canonical_json)
    return CallConfigResponse(
        call_logical_id=call_logical_id,
        config_version="1",
        ui_mode="structured_nodes",
        expected_nodes=expected_nodes,
        domain_options=domain_options,
        split_visibility_reviewability_enabled=split_opt_in_enabled,
    )


@app.get(
    "/calls/{call_id}/nodes",
    response_model=NodesResponse | NodesTreeResponse,
    responses=API_ERROR_RESPONSES,
)
def list_call_nodes(
    call_id: UUID,
    repository: RepositoryDep,
    view: Literal["flat", "tree"] = Query(default="flat"),
) -> NodesResponse | NodesTreeResponse:
    """List proposal nodes for a call in flat or tree view."""
    call = repository.get_call_by_id(call_id)
    if call is None:
        raise APIException(code="CALL_NOT_FOUND", message="Funding call not found.")

    definition = repository.get_call_definition_by_call_id(call_id)
    split_opt_in_enabled = False
    node_roles_by_logical_id: dict[str, Literal["PRIMARY", "SUPPORTING"]] = {}
    if definition is not None:
        split_opt_in_enabled = _is_split_visibility_reviewability_enabled(
            definition.canonical_json
        )
        node_roles_by_logical_id = _extract_node_roles_by_logical_id(
            canonical_json=definition.canonical_json,
            split_opt_in_enabled=split_opt_in_enabled,
        )

    nodes = repository.get_nodes_for_call(call_id)
    flat_nodes = [
        NodeSummary(
            id=node.id,
            logical_id=node.logical_id,
            parent_node_id=node.parent_node_id,
            title=node.title,
            node_type=node.node_type,
            order_index=node.order_index,
            has_expectations=has_expectations,
            node_role=(
                node_roles_by_logical_id.get(node.logical_id)
                if split_opt_in_enabled and isinstance(node.logical_id, str)
                else None
            ),
        )
        for node, has_expectations in nodes
    ]

    if view == "flat":
        return NodesResponse(nodes=flat_nodes)

    if definition is not None:
        try:
            canonical_tree = NodeTreeService().build_tree_from_canonical(
                definition.canonical_json,
                flat_nodes,
            )
        except NodeTreeMismatchError as err:
            raise APIException(
                code="CALL_DEFINITION_NODE_MISMATCH",
                message="Call definition references nodes that do not map to active call nodes.",
                details={"node_logical_ids": err.node_logical_ids},
            ) from err
        except NodeTreeCycleError as err:
            raise APIException(
                code="CALL_DEFINITION_CYCLE",
                message="Call definition contains a cycle in parent_logical_id links.",
            ) from err

        if canonical_tree is not None:
            return NodesTreeResponse(nodes=canonical_tree)

    nodes_by_parent: dict[UUID | None, list[NodeSummary]] = {}
    for node in flat_nodes:
        nodes_by_parent.setdefault(node.parent_node_id, []).append(node)

    def build_tree(parent_id: UUID | None) -> list[NodeTreeNode]:
        ordered_children = nodes_by_parent.get(parent_id, [])
        return [
            NodeTreeNode(
                id=child.id,
                logical_id=child.logical_id,
                parent_node_id=child.parent_node_id,
                title=child.title,
                node_type=child.node_type,
                order_index=child.order_index,
                has_expectations=child.has_expectations,
                node_role=child.node_role,
                children=build_tree(child.id),
            )
            for child in ordered_children
        ]

    return NodesTreeResponse(nodes=build_tree(parent_id=None))


@app.get(
    "/api/public/calls/{call_logical_id}/nodes/metadata",
    response_model=NodeMetadataResponse,
    responses=API_ERROR_RESPONSES,
)
def get_call_nodes_metadata(
    call_logical_id: str,
    repository: RepositoryDep,
    node_logical_ids: list[str] | None = NODE_LOGICAL_IDS_QUERY,
) -> NodeMetadataResponse:
    """Return node metadata DTOs for universal-form rendering."""
    call = repository.get_active_call_by_code(call_logical_id)
    if call is None:
        raise APIException(code="CALL_NOT_FOUND", message="Funding call not found.")

    definition = repository.get_call_definition_by_call_id(call.id)
    if definition is None:
        raise APIException(
            code="CALL_DEFINITION_MISSING",
            message="Call definition is required for metadata endpoint.",
        )

    return NodeMetadataService().build_metadata_response(
        call=call,
        definition=definition,
        node_logical_ids=node_logical_ids,
        repository=repository,
    )


@app.post(
    "/api/check-compliance",
    response_model=ComplianceCheckResponse,
    responses=API_ERROR_RESPONSES,
)
def check_compliance(
    payload: ComplianceCheckRequest,
    repository: RepositoryDep,
    _: Annotated[str, Depends(require_bff_user_id)],
) -> ComplianceCheckResponse:
    """Run deterministic compliance checks for a structured draft payload."""
    call = repository.get_call_by_id(payload.call_id)
    if call is None:
        raise APIException(code="CALL_NOT_FOUND", message="Funding call not found.")
    call_definition = repository.get_call_definition_by_call_id(payload.call_id)

    hydrated_nodes = CallDefinitionService(repository.session).get_hydrated_nodes(
        payload.call_id
    )
    available_node_ids = {
        node.node.logical_id
        for node in hydrated_nodes
        if isinstance(node.node.logical_id, str)
    }

    submitted_ids = [item.node_logical_id for item in payload.draft_nodes]
    seen_ids: set[str] = set()
    duplicates: set[str] = set()
    for node_id in submitted_ids:
        if node_id in seen_ids:
            duplicates.add(node_id)
        else:
            seen_ids.add(node_id)
    if duplicates:
        raise APIException(
            code="DUPLICATE_NODE_ID",
            message="Duplicate node_logical_id values are not allowed.",
            details={"node_logical_ids": sorted(duplicates)},
        )

    unknown_ids = sorted(set(submitted_ids) - available_node_ids)
    if unknown_ids:
        raise APIException(
            code="UNKNOWN_NODE_ID",
            message="One or more node_logical_id values are unknown for this call.",
            details={"node_logical_ids": unknown_ids},
        )
    supporting_node_ids = resolve_supporting_node_logical_ids_for_primary_path(
        call_definition
    )
    submitted_supporting_ids = find_supporting_node_ids_in_primary_path_draft(
        payload,
        supporting_node_ids,
    )
    if submitted_supporting_ids:
        raise APIException(
            code="SUPPORTING_NODE_NOT_ALLOWED",
            message="Supporting node_logical_id values are not allowed for primary review path.",
            details={"node_logical_ids": submitted_supporting_ids},
        )

    normalized_domain = _normalize_domain(payload.domain)
    domain_limited_nodes = [
        node for node in hydrated_nodes if _is_domain_limited_node(node.config)
    ]
    requires_domain = any(
        not _has_domain_default_fallback(node.config) for node in domain_limited_nodes
    )
    if requires_domain and normalized_domain is None:
        raise APIException(
            code="DOMAIN_REQUIRED",
            message="domain is required for this call.",
        )

    known_domains: set[str] = set()
    for hydrated in domain_limited_nodes:
        known_domains.update(_extract_known_domains(hydrated.config))
    if normalized_domain and known_domains and normalized_domain not in known_domains:
        raise APIException(
            code="DOMAIN_INVALID",
            message="domain is not recognized for this call.",
            details={"domain": normalized_domain, "allowed": sorted(known_domains)},
        )

    normalized_payload = ComplianceCheckRequest(
        call_id=payload.call_id,
        domain=normalized_domain,
        draft_nodes=payload.draft_nodes,
    )
    started = time.perf_counter()
    report = evaluate_compliance(normalized_payload, hydrated_nodes)
    elapsed_ms = (time.perf_counter() - started) * 1000.0
    if elapsed_ms > 500:
        logger.warning("Compliance evaluation took %.2fms", elapsed_ms)
    return report


@app.post(
    "/api/structured-review",
    response_model=CreateReviewResponse,
    response_model_exclude_none=True,
    responses=API_ERROR_RESPONSES,
)
def create_structured_review(
    payload: StructuredReviewRequest,
    repository: RepositoryDep,
    external_user_id: Annotated[str, Depends(require_bff_user_id)],
    request: Request,
    response: Response,
) -> CreateReviewResponse:
    """Create a structured multi-node review synchronously."""
    idempotency_key = request.headers.get("Idempotency-Key", "").strip()
    if not idempotency_key:
        raise APIException(
            code="VALIDATION_ERROR",
            message="Missing required Idempotency-Key header.",
        )

    call = repository.get_call_by_id(payload.call_id)
    if call is None:
        raise APIException(code="CALL_NOT_FOUND", message="Funding call not found.")
    support_trace = _build_wf0080_support_trace_metadata(
        call_code=call.code,
        external_user_id=external_user_id,
        idempotency_key=idempotency_key,
    )
    _set_support_trace_header(response, support_trace)

    payload_json = json.dumps(
        payload.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
    )
    request_payload_sha256 = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()
    now = datetime.now(UTC)

    existing_review = repository.get_active_review_by_idempotency(
        external_user_id=external_user_id,
        idempotency_key=idempotency_key,
        at_time=now,
    )
    if existing_review is not None:
        if existing_review.request_payload_sha256 != request_payload_sha256:
            raise APIException(
                code="IDEMPOTENCY_PAYLOAD_MISMATCH",
                message="Idempotency key was already used with a different payload.",
            )
        return CreateReviewResponse(
            review_id=existing_review.id,
            status=existing_review.status,
            support_trace=support_trace,
        )

    if not _is_reviews_enabled():
        raise APIException(
            code="REVIEWS_DISABLED",
            message="Reviews are temporarily disabled.",
        )

    day_start = datetime(now.year, now.month, now.day, tzinfo=UTC)
    day_end = day_start + timedelta(days=1)
    free_daily_limit = _get_free_daily_review_limit()
    used_today = repository.count_reviews_for_external_user_between(
        external_user_id=external_user_id,
        start_time=day_start,
        end_time=day_end,
    )
    if used_today >= free_daily_limit:
        raise APIException(
            code="QUOTA_EXCEEDED",
            message="Daily review quota exceeded.",
            details={
                "limit": free_daily_limit,
                "remaining": 0,
                "reset_at": day_end.isoformat(),
            },
        )

    call_definition = repository.get_call_definition_by_call_id(payload.call_id)

    if not payload.nodes:
        raise APIException(
            code="STRUCTURED_NODES_REQUIRED",
            message="At least one node is required.",
        )

    total_chars = 0
    duplicates: set[str] = set()
    seen: set[str] = set()
    for node in payload.nodes:
        total_chars += len(node.text)
        if len(node.text) > MAX_NODE_TEXT_CHARS:
            raise APIException(
                code="STRUCTURED_PAYLOAD_TOO_LARGE",
                message=(
                    f"Node '{node.node_logical_id}' exceeds max length of "
                    f"{MAX_NODE_TEXT_CHARS} characters."
                ),
            )
        if node.node_logical_id in seen:
            duplicates.add(node.node_logical_id)
        else:
            seen.add(node.node_logical_id)
    if duplicates:
        raise APIException(
            code="DUPLICATE_NODE_ID",
            message="Duplicate node_logical_id values are not allowed.",
            details={"node_logical_ids": sorted(duplicates)},
        )
    if total_chars > MAX_STRUCTURED_PAYLOAD_CHARS:
        raise APIException(
            code="STRUCTURED_PAYLOAD_TOO_LARGE",
            message=(
                "Structured payload exceeds max total length of "
                f"{MAX_STRUCTURED_PAYLOAD_CHARS} characters."
            ),
            details={"max_chars": MAX_STRUCTURED_PAYLOAD_CHARS},
        )

    available_node_ids = {
        node.logical_id
        for node, _ in repository.get_nodes_for_call(payload.call_id)
        if isinstance(node.logical_id, str)
    }
    submitted_node_ids = [node.node_logical_id for node in payload.nodes]
    unknown_ids = sorted(set(submitted_node_ids) - available_node_ids)
    if unknown_ids:
        raise APIException(
            code="UNKNOWN_NODE_ID",
            message="One or more node_logical_id values are unknown for this call.",
            details={"node_logical_ids": unknown_ids},
        )

    stage_mismatch_ids = sorted(
        node.node_logical_id
        for node in payload.nodes
        if not matches_review_stage(
            node_logical_id=node.node_logical_id,
            review_stage=payload.review_stage,
            call_definition=call_definition,
        )
    )
    if stage_mismatch_ids:
        raise APIException(
            code="REVIEW_STAGE_NODE_MISMATCH",
            message="One or more nodes do not belong to selected review_stage.",
            details={
                "review_stage": payload.review_stage,
                "node_logical_ids": stage_mismatch_ids,
            },
        )
    supporting_node_ids = resolve_supporting_node_logical_ids_for_primary_path(
        call_definition
    )
    submitted_supporting_ids = sorted(
        {node.node_logical_id for node in payload.nodes if node.node_logical_id in supporting_node_ids}
    )
    if submitted_supporting_ids:
        raise APIException(
            code="SUPPORTING_NODE_NOT_ALLOWED",
            message="Supporting node_logical_id values are not allowed for primary review path.",
            details={"node_logical_ids": submitted_supporting_ids},
        )

    reviewer_service = StructuredReviewerService(
        repository=repository,
        llm_client=build_llm_client(),
    )
    try:
        selected_engine_path = "pipeline_v1"
        review, _ = reviewer_service.generate_structured_review_pipeline_v1(
            review_stage=payload.review_stage,
            call_id=payload.call_id,
            nodes=[(node.node_logical_id, node.text) for node in payload.nodes],
            external_user_id=external_user_id,
            idempotency_key=idempotency_key,
            request_payload_sha256=request_payload_sha256,
            idempotency_expires_at=now + timedelta(hours=IDEMPOTENCY_TTL_HOURS),
        )
        logger.info(
            "structured_review.engine_path=%s call_code=%s review_id=%s",
            selected_engine_path,
            call.code,
            review.id,
        )
    except IntegrityError as err:
        if not is_idempotency_conflict_error(err):
            raise APIException(
                code="INTERNAL_ERROR",
                message="Database integrity error during review creation.",
            ) from err

        repository.rollback()
        existing_on_conflict = (
            repository.get_review_by_external_user_and_idempotency_key(
                external_user_id=external_user_id,
                idempotency_key=idempotency_key,
            )
        )
        if existing_on_conflict is None:
            raise APIException(
                code="INTERNAL_ERROR",
                message="Idempotency conflict handling failed.",
            ) from err
        if existing_on_conflict.request_payload_sha256 != request_payload_sha256:
            raise APIException(
                code="IDEMPOTENCY_PAYLOAD_MISMATCH",
                message="Idempotency key was already used with a different payload.",
            ) from err
        return CreateReviewResponse(
            review_id=existing_on_conflict.id,
            status=existing_on_conflict.status,
            support_trace=support_trace,
        )
    except ValueError as err:
        raise APIException(code="VALIDATION_ERROR", message=str(err)) from err

    return CreateReviewResponse(
        review_id=review.id,
        status=review.status,
        support_trace=support_trace,
    )


@app.post(
    "/reviews",
    response_model=CreateReviewResponse,
    responses=API_ERROR_RESPONSES,
)
def create_review(
    payload: CreateReviewRequest,
    repository: RepositoryDep,
    external_user_id: Annotated[str, Depends(require_bff_user_id)],
    request: Request,
) -> CreateReviewResponse:
    """Create a review synchronously."""
    idempotency_key = request.headers.get("Idempotency-Key", "").strip()
    if not idempotency_key:
        raise APIException(
            code="VALIDATION_ERROR",
            message="Missing required Idempotency-Key header.",
        )

    payload_json = json.dumps(
        payload.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
    )
    request_payload_sha256 = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()
    now = datetime.now(UTC)

    existing_review = repository.get_active_review_by_idempotency(
        external_user_id=external_user_id,
        idempotency_key=idempotency_key,
        at_time=now,
    )
    if existing_review is not None:
        if existing_review.request_payload_sha256 != request_payload_sha256:
            raise APIException(
                code="IDEMPOTENCY_PAYLOAD_MISMATCH",
                message="Idempotency key was already used with a different payload.",
            )
        return CreateReviewResponse(
            review_id=existing_review.id,
            status=existing_review.status,
        )

    if not _is_reviews_enabled():
        raise APIException(
            code="REVIEWS_DISABLED",
            message="Reviews are temporarily disabled.",
        )

    day_start = datetime(now.year, now.month, now.day, tzinfo=UTC)
    day_end = day_start + timedelta(days=1)
    free_daily_limit = _get_free_daily_review_limit()
    used_today = repository.count_reviews_for_external_user_between(
        external_user_id=external_user_id,
        start_time=day_start,
        end_time=day_end,
    )
    if used_today >= free_daily_limit:
        raise APIException(
            code="QUOTA_EXCEEDED",
            message="Daily review quota exceeded.",
            details={
                "limit": free_daily_limit,
                "remaining": 0,
                "reset_at": day_end.isoformat(),
            },
        )

    if len(payload.snippet_text) > MAX_SNIPPET_CHARS:
        raise APIException(
            code="SNIPPET_TOO_LONG",
            message=f"Snippet exceeds max length of {MAX_SNIPPET_CHARS} characters.",
            details={"max_chars": MAX_SNIPPET_CHARS},
        )

    call = repository.get_call_by_id(payload.call_id)
    if call is None:
        raise APIException(code="CALL_NOT_FOUND", message="Funding call not found.")
    call_definition = repository.get_call_definition_by_call_id(payload.call_id)

    node = repository.get_node_by_id(payload.node_id)
    if node is None:
        raise APIException(code="NODE_NOT_FOUND", message="Proposal node not found.")
    if node.funding_call_id != payload.call_id:
        raise APIException(
            code="NODE_NOT_IN_CALL",
            message="Selected node does not belong to selected call.",
        )
    if not matches_review_stage(
        node_logical_id=node.logical_id,
        review_stage=payload.review_stage,
        call_definition=call_definition,
    ):
        raise APIException(
            code="REVIEW_STAGE_NODE_MISMATCH",
            message="Selected node does not belong to selected review_stage.",
            details={
                "review_stage": payload.review_stage,
                "node_id": str(payload.node_id),
                "node_logical_id": node.logical_id,
            },
        )

    reviewer_service = ReviewerService(
        repository=repository,
        llm_client=build_llm_client(),
    )
    try:
        review, _ = reviewer_service.generate_review(
            node_id=payload.node_id,
            snippet_text=payload.snippet_text,
            call_id=payload.call_id,
            review_stage=payload.review_stage,
            external_user_id=external_user_id,
            idempotency_key=idempotency_key,
            request_payload_sha256=request_payload_sha256,
            idempotency_expires_at=now + timedelta(hours=IDEMPOTENCY_TTL_HOURS),
        )
    except IntegrityError as err:
        repository.rollback()
        existing_on_conflict = (
            repository.get_review_by_external_user_and_idempotency_key(
                external_user_id=external_user_id,
                idempotency_key=idempotency_key,
            )
        )
        if existing_on_conflict is None:
            raise APIException(
                code="INTERNAL_ERROR",
                message="Idempotency conflict handling failed.",
            ) from err
        if existing_on_conflict.request_payload_sha256 != request_payload_sha256:
            raise APIException(
                code="IDEMPOTENCY_PAYLOAD_MISMATCH",
                message="Idempotency key was already used with a different payload.",
            ) from err
        return CreateReviewResponse(
            review_id=existing_on_conflict.id,
            status=existing_on_conflict.status,
        )
    except ValueError as err:
        raise map_review_failure_to_api_error(err) from err

    return CreateReviewResponse(review_id=review.id, status=review.status)


@app.get(
    "/reviews",
    response_model=ReviewsListResponse,
    responses=API_ERROR_RESPONSES,
)
def list_reviews(
    repository: RepositoryDep,
    external_user_id: Annotated[str, Depends(require_bff_user_id)],
    limit: int = 50,
) -> ReviewsListResponse:
    """List reviews for the authenticated user."""
    rows = repository.list_reviews_for_external_user(
        external_user_id,
        limit=limit,
    )
    return ReviewsListResponse(
        reviews=[
            ReviewListItem(
                id=review.id,
                status=review.status,
                overall_rating=review.overall_rating,
                created_at=review.created_at.isoformat(),
                call_name=call_name,
                node_title=node_title,
            )
            for review, call_name, node_title in rows
        ],
    )


@app.get(
    "/reviews/{review_id}",
    response_model=ReviewDetailResponse,
    response_model_exclude_none=True,
    responses=API_ERROR_RESPONSES,
)
def get_review(
    review_id: UUID,
    repository: RepositoryDep,
    external_user_id: Annotated[str, Depends(require_bff_user_id)],
) -> ReviewDetailResponse:
    """Fetch review details and ordered cards."""
    review = repository.get_review_by_id(review_id)
    if review is None:
        raise APIException(code="REVIEW_NOT_FOUND", message="Review not found.")

    review_owner_external_user_id = repository.get_review_owner_external_user_id(
        review_id
    )
    if review_owner_external_user_id != external_user_id:
        logger.warning(
            "OWNERSHIP_VIOLATION: review_id=%s requested_by=%s owner=%s",
            review_id,
            external_user_id,
            review_owner_external_user_id,
        )
        raise APIException(code="REVIEW_NOT_FOUND", message="Review not found.")

    cards_with_criteria = []
    if review.status == ReviewStatus.COMPLETED or (
        review.status == ReviewStatus.FAILED and review.review_type == "structured"
    ):
        cards_with_criteria = repository.get_review_cards_with_criteria(review_id)

    call_id = _resolve_review_call_id(review, repository)
    call = repository.get_call_by_id(call_id) if call_id is not None else None
    submitted_node_logical_ids = repository.get_submitted_node_logical_ids_for_review(review)
    criterion_source_hints: dict[str, str] = {}
    element_source_hints: dict[str, str] = {}
    if call_id is not None:
        call_definition = repository.get_call_definition_by_call_id(call_id)
        if call_definition is not None and isinstance(call_definition.canonical_json, dict):
            criterion_source_hints, element_source_hints = (
                _extract_source_hints_by_logical_id(call_definition.canonical_json)
            )

    cards: list[ReviewCardSummary] = []
    for (
        card,
        criterion_name,
        criterion_desc,
        element_name,
        guidance_note,
        node_logical_id,
        node_title,
        criterion_logical_id,
        element_logical_id,
    ) in cards_with_criteria:
        source_basis_label, source_basis_state = _resolve_card_source_basis(
            has_call_linkage=call_id is not None,
            criterion_logical_id=criterion_logical_id,
            element_logical_id=element_logical_id,
            criterion_hints=criterion_source_hints,
            element_hints=element_source_hints,
        )
        cards.append(
            ReviewCardSummary(
                id=card.id,
                node_expectation_id=card.node_expectation_id,
                node_logical_id=node_logical_id,
                node_title=node_title,
                criterion=criterion_name,
                criterion_description=criterion_desc,
                evaluation_element_name=element_name,
                expectation_guidance_note=guidance_note,
                rating=card.rating,
                feedback_text=card.feedback_text,
                synthesized_companion_text=card.synthesized_companion_text,
                assessment_status=(
                    card.assessment_status if review.review_type == "structured" else None
                ),
                not_assessable_reason=(
                    card.not_assessable_reason
                    if review.review_type == "structured"
                    else None
                ),
                source_basis_label=source_basis_label,
                source_basis_state=source_basis_state,
            )
        )

    ordering_source: Literal["call_nodes", "review_payload_fallback"] = (
        "review_payload_fallback"
    )
    unmapped_node_logical_ids: list[str] = []
    if call_id is not None:
        order_map = _build_call_order_index_map(call_id, repository)
        cards, unmapped_node_logical_ids = _order_review_cards(cards, order_map=order_map)
        ordering_source = "call_nodes"
    detail_state = _infer_review_detail_state(
        call_id=call_id,
        call_code=call.code if call is not None else None,
        ordering_source=ordering_source,
        unmapped_node_logical_ids=unmapped_node_logical_ids,
    )
    submitted_leaf_ids, legacy_ambiguous_container_ids, moved_legacy_node_references = (
        repository.resolve_structured_review_coverage(review)
    )
    (
        primary_evaluated_node_logical_ids,
        supporting_context_node_logical_ids,
    ) = repository.resolve_review_detail_role_labels(review=review, call_id=call_id)
    reviewed_card_node_logical_ids = sorted(
        {
            card.node_logical_id
            for card in cards
            if isinstance(card.node_logical_id, str)
        }
    )
    (
        visible_not_reviewed_node_logical_ids,
        no_generated_cards_node_logical_ids,
    ) = repository.resolve_review_detail_boundary_metadata(
        call_id=call_id,
        submitted_leaf_ids=submitted_leaf_ids,
        reviewed_card_node_logical_ids=reviewed_card_node_logical_ids,
    )
    # WF-0070 Task 7: Derive out-of-scope nodes from persisted stage_scope_leaf_ids.
    visible_not_reviewed_node_logical_ids, out_of_scope_node_logical_ids = (
        _partition_visible_by_stage_scope(
            visible_not_reviewed=visible_not_reviewed_node_logical_ids,
            structured_payload=review.structured_payload,
        )
    )
    compatibility_notes: list[ReviewCompatibilityNote] = []
    if legacy_ambiguous_container_ids:
        compatibility_notes.append(
            ReviewCompatibilityNote(
                note_type="deprecated_container_submission",
                node_logical_ids=legacy_ambiguous_container_ids,
                message="Deprecated container submissions are preserved as ambiguous legacy evidence.",
            )
        )
    if moved_legacy_node_references:
        compatibility_notes.append(
            ReviewCompatibilityNote(
                note_type="moved_legacy_node_reference",
                node_logical_ids=moved_legacy_node_references,
                message="Legacy moved-node references were mapped to corrected leaf identities.",
            )
        )
    if submitted_leaf_ids and legacy_ambiguous_container_ids:
        compatibility_notes.append(
            ReviewCompatibilityNote(
                note_type="mixed_version_review",
                node_logical_ids=sorted(
                    [*submitted_leaf_ids, *legacy_ambiguous_container_ids]
                ),
                message="Mixed-version review detected; corrected leaf IDs remain the only proven reviewed coverage.",
            )
        )
    detail_projection = (
        _build_wf0080_detail_projection(cards)
        if _is_wf0080_launch_wedge_call(call.code if call is not None else None)
        else None
    )
    support_trace = _build_wf0080_support_trace_metadata(
        call_code=call.code if call is not None else None,
        external_user_id=review.external_user_id,
        idempotency_key=review.idempotency_key,
    )

    return ReviewDetailResponse(
        call_id=call_id,
        call_code=call.code if call is not None else None,
        submitted_node_logical_ids=submitted_node_logical_ids,
        detail_state=detail_state,
        ordering_source=ordering_source,
        unmapped_node_logical_ids=unmapped_node_logical_ids,
        submitted_leaf_ids=submitted_leaf_ids,
        primary_evaluated_node_logical_ids=primary_evaluated_node_logical_ids,
        supporting_context_node_logical_ids=supporting_context_node_logical_ids,
        visible_not_reviewed_node_logical_ids=visible_not_reviewed_node_logical_ids,
        out_of_scope_node_logical_ids=out_of_scope_node_logical_ids,
        no_generated_cards_node_logical_ids=no_generated_cards_node_logical_ids,
        legacy_ambiguous_container_ids=legacy_ambiguous_container_ids,
        moved_legacy_node_references=moved_legacy_node_references,
        compatibility_notes=compatibility_notes,
        detail_projection=detail_projection,
        support_trace=support_trace,
        review=ReviewSummary(
            id=review.id,
            status=review.status,
            overall_rating=review.overall_rating,
            overall_summary=review.overall_summary,
        ),
        cards=cards,
    )


@app.delete(
    "/reviews/{review_id}",
    response_model=DeleteReviewResponse,
    responses=API_ERROR_RESPONSES,
)
def delete_review(
    review_id: UUID,
    repository: RepositoryDep,
    external_user_id: Annotated[str, Depends(require_bff_user_id)],
) -> DeleteReviewResponse:
    """Hard-delete a review and associated data for its owner."""
    review = repository.get_review_by_id(review_id)
    if review is None:
        raise APIException(code="REVIEW_NOT_FOUND", message="Review not found.")

    review_owner_external_user_id = repository.get_review_owner_external_user_id(
        review_id
    )
    if review_owner_external_user_id != external_user_id:
        logger.warning(
            "OWNERSHIP_VIOLATION: delete review_id=%s requested_by=%s owner=%s",
            review_id,
            external_user_id,
            review_owner_external_user_id,
        )
        raise APIException(code="REVIEW_NOT_FOUND", message="Review not found.")

    repository.delete_review_hard(review_id)
    return DeleteReviewResponse(ok=True)
