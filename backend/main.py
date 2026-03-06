"""FastAPI entrypoint for Grant Reviewer backend."""

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
from fastapi import Depends, FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.db import create_db_and_tables, get_session, ping_database
from app.models.domain import ProposalSnippet, ReviewStatus
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
    ReviewDetailResponse,
    ReviewListItem,
    ReviewsListResponse,
    ReviewSummary,
)
from app.schemas.compliance import ComplianceCheckRequest, ComplianceCheckResponse
from app.schemas.structured_review import (
    MAX_NODE_TEXT_CHARS,
    MAX_STRUCTURED_PAYLOAD_CHARS,
    StructuredReviewRequest,
)
from app.services.call_definition_service import CallDefinitionService
from app.services.compliance_engine import evaluate_compliance
from app.services.llm_client import build_llm_client
from app.services.node_metadata_service import NodeMetadataService
from app.services.node_tree_service import (
    NodeTreeCycleError,
    NodeTreeMismatchError,
    NodeTreeService,
)
from app.services.reviewer_policy import matches_review_stage
from app.services.reviewer_service import ReviewerService
from app.services.structured_reviewer_service import StructuredReviewerService

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
    ) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
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
) -> JSONResponse:
    """Build canonical error JSON response."""
    payload = APIErrorResponse(
        error=APIErrorBody(code=code, message=message, details=details or {}),
    )
    status_code = ERROR_STATUS_BY_CODE.get(code, 500)
    return JSONResponse(
        status_code=status_code, content=payload.model_dump(mode="json")
    )


@app.exception_handler(APIException)
async def api_exception_handler(_: Request, exc: APIException) -> JSONResponse:
    """Handle known API exceptions."""
    return build_error_response(code=exc.code, message=exc.message, details=exc.details)


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
    raw = os.getenv("FREE_DAILY_REVIEW_LIMIT", str(FREE_DAILY_REVIEW_LIMIT)).strip()
    try:
        return max(0, int(raw))
    except ValueError:
        logger.warning(
            "Invalid FREE_DAILY_REVIEW_LIMIT=%s; falling back to default", raw
        )
        return FREE_DAILY_REVIEW_LIMIT


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
        )

    canonical_json = definition.canonical_json
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
        )

    domain_options = _extract_domain_options(canonical_json)
    return CallConfigResponse(
        call_logical_id=call_logical_id,
        config_version="1",
        ui_mode="structured_nodes",
        expected_nodes=expected_nodes,
        domain_options=domain_options,
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
        )
        for node, has_expectations in nodes
    ]

    if view == "flat":
        return NodesResponse(nodes=flat_nodes)

    definition = repository.get_call_definition_by_call_id(call_id)
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
    responses=API_ERROR_RESPONSES,
)
def create_structured_review(
    payload: StructuredReviewRequest,
    repository: RepositoryDep,
    external_user_id: Annotated[str, Depends(require_bff_user_id)],
    request: Request,
) -> CreateReviewResponse:
    """Create a structured multi-node review synchronously."""
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

    call = repository.get_call_by_id(payload.call_id)
    if call is None:
        raise APIException(code="CALL_NOT_FOUND", message="Funding call not found.")

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
        )
    except ValueError as err:
        raise APIException(code="VALIDATION_ERROR", message=str(err)) from err

    return CreateReviewResponse(review_id=review.id, status=review.status)


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
    submitted_node_logical_ids = repository.get_submitted_node_logical_ids_for_review(
        review
    )
    cards = [
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
            assessment_status=(
                card.assessment_status if review.review_type == "structured" else None
            ),
            not_assessable_reason=(
                card.not_assessable_reason if review.review_type == "structured" else None
            ),
        )
        for (
            card,
            criterion_name,
            criterion_desc,
            element_name,
            guidance_note,
            node_logical_id,
            node_title,
        ) in cards_with_criteria
    ]

    ordering_source: Literal["call_nodes", "review_payload_fallback"] = (
        "review_payload_fallback"
    )
    unmapped_node_logical_ids: list[str] = []
    if call_id is not None:
        order_map = _build_call_order_index_map(call_id, repository)
        cards, unmapped_node_logical_ids = _order_review_cards(cards, order_map=order_map)
        ordering_source = "call_nodes"

    return ReviewDetailResponse(
        call_id=call_id,
        call_code=call.code if call is not None else None,
        submitted_node_logical_ids=submitted_node_logical_ids,
        ordering_source=ordering_source,
        unmapped_node_logical_ids=unmapped_node_logical_ids,
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
