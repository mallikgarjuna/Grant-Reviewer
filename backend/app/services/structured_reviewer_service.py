"""backend/app/services/structured_reviewer_service.py
Structured review service for multi-node proposal assessments.
"""

from __future__ import annotations

import hashlib
import logging
import os
from datetime import datetime
from uuid import UUID

from app.engine.contracts import PipelineResult
from app.engine.errors import EngineContractError, EngineErrorCode
from app.engine.pipeline_v1 import run_review_pipeline
from app.engine.review_request_validator import (
    ReviewRequestValidationError,
    canonicalize_for_digest,
    validate_review_request_payload,
)
from app.models.domain import (
    AssessmentStatus,
    NodeExpectation,
    Review,
    ReviewCard,
    ReviewRating,
    ReviewStatus,
)
from app.repositories.review_repository import ReviewRepository
from app.services.llm_client import LLMClientProtocol, OpenAIClient
from app.services.node_role_resolution import (
    resolve_supporting_node_logical_ids_for_primary_path,
)
from app.services.review_execution_core import ReviewExecutionCore
from app.services.reviewer_policy import (
    ReviewerPolicyRule,
    ReviewStage,
    find_policy_violations,
    get_applicable_reviewer_policy_rules,
)

logger = logging.getLogger(__name__)

ALIGNMENT_ELEMENT_IDS = {
    "elem_cv_idea_alignment",
    "elem_alignment_plan_credibility",
}
ALIGNMENT_REQUIRED_NODES = ("academic_profile", "key_outputs")
STRUCTURED_SUMMARY_COMPLETED_PREFIX = "Structured review completed with"
STRUCTURED_POLICY_BLOCKING_PREFIX = "POLICY_BLOCKING:"
STRUCTURED_POLICY_WARNING_PREFIX = "Reviewer-policy warnings:"
WF0060_ERC_CONTAINER_NODE_IDS = {"part_a", "budget", "part_b", "b1", "b2"}
WF0069_ACTIONABILITY_CALL_CODES = {"nwo_veni_2025_preproposal"}


class StructuredReviewerService:
    """Service for generating structured multi-node reviews."""

    def __init__(
        self,
        repository: ReviewRepository,
        llm_client: LLMClientProtocol | None = None,
        execution_core: ReviewExecutionCore | None = None,
    ) -> None:
        self.repository = repository
        self._llm_client = llm_client
        self._timeout_seconds = float(os.getenv("REVIEW_TIMEOUT_SECONDS", "30"))
        self._execution_core = execution_core

    @property
    def llm_client(self) -> LLMClientProtocol:
        """Lazy-load LLM client."""
        if self._llm_client is None:
            self._llm_client = OpenAIClient()
        return self._llm_client

    @property
    def execution_core(self) -> ReviewExecutionCore:
        if self._execution_core is None:
            self._execution_core = ReviewExecutionCore(
                llm_client=self.llm_client,
                timeout_seconds=self._timeout_seconds,
            )
        return self._execution_core

    def _partition_expectations(
        self,
        *,
        node_logical_id: str,
        expectations: list[NodeExpectation],
        submitted_text_by_node: dict[str, str],
    ) -> tuple[list[NodeExpectation], list[tuple[NodeExpectation, str]]]:
        assessable: list[NodeExpectation] = []
        not_assessable: list[tuple[NodeExpectation, str]] = []

        for expectation in expectations:
            if not self._needs_alignment_context(node_logical_id, expectation):
                assessable.append(expectation)
                continue

            missing_nodes = [
                upstream_node
                for upstream_node in ALIGNMENT_REQUIRED_NODES
                if not submitted_text_by_node.get(upstream_node, "").strip()
            ]
            if missing_nodes:
                not_assessable.append(
                    (
                        expectation,
                        "Missing required context from: " + ", ".join(missing_nodes),
                    )
                )
            else:
                assessable.append(expectation)

        return assessable, not_assessable

    def generate_structured_review_pipeline_v1(
        self,
        *,
        review_stage: ReviewStage,
        call_id: UUID,
        nodes: list[tuple[str, str]],
        external_user_id: str,
        idempotency_key: str | None = None,
        request_payload_sha256: str | None = None,
        idempotency_expires_at: datetime | None = None,
        call_config_digest_override: str | None = None,
    ) -> tuple[Review, list[ReviewCard]]:
        if not nodes:
            raise ValueError("At least one node is required.")

        template = self.repository.get_active_prompt_template()
        if template is None:
            raise ValueError("No active prompt template found.")

        call = self.repository.get_call_by_id(call_id)
        if call is None:
            raise ValueError("Funding call not found.")
        call_definition = self.repository.get_call_definition_by_call_id(call_id)
        supporting_node_ids = resolve_supporting_node_logical_ids_for_primary_path(
            call_definition
        )
        submitted_supporting_ids = sorted(
            {node_logical_id for node_logical_id, _ in nodes if node_logical_id in supporting_node_ids}
        )
        if submitted_supporting_ids:
            raise ValueError(
                "Supporting node_logical_id values are not allowed for primary review path: "
                + ", ".join(submitted_supporting_ids)
            )

        call_nodes = self.repository.get_nodes_for_call(call_id)
        node_by_logical_id = {
            node.logical_id: node
            for node, _ in call_nodes
            if isinstance(node.logical_id, str) and node.logical_id
        }
        submitted_text_by_node = {node_logical_id: text for node_logical_id, text in nodes}
        submitted_leaf_ids = [node_logical_id for node_logical_id, _ in nodes]
        structured_payload = {
            "call_id": str(call_id),
            "call_name": call.name,
            "review_stage": review_stage,
            "nodes": submitted_text_by_node,
            "submitted_leaf_ids": submitted_leaf_ids,
            "legacy_ambiguous_container_ids": [],
            "moved_legacy_node_references": [],
            "engine_path": "pipeline_v1",
        }

        review = self.repository.create_review(
            template_id=template.id,
            snippet_id=None,
            external_user_id=external_user_id,
            idempotency_key=idempotency_key,
            request_payload_sha256=request_payload_sha256,
            idempotency_expires_at=idempotency_expires_at,
            review_type="structured",
            structured_payload=structured_payload,
        )
        review.llm_model = "engine-pipeline-v1"
        self.repository.update_review(review)

        expectation_map: dict[str, NodeExpectation] = {}
        not_assessable_payloads: list[
            tuple[UUID, ReviewRating, str, AssessmentStatus, str | None]
        ] = []
        request_expectations: list[dict[str, object]] = []
        applicable_policy_by_node: dict[str, list[ReviewerPolicyRule]] = {}
        for node_logical_id, _ in nodes:
            node = node_by_logical_id.get(node_logical_id)
            if node is None:
                return self._fail_contract_error(
                    review,
                    code=EngineErrorCode.MALFORMED_REVIEW_REQUEST.value,
                    message=f"Unknown node_logical_id: '{node_logical_id}'",
                )
            if (
                call.code == "erc_stg_2026_full"
                and node_logical_id in WF0060_ERC_CONTAINER_NODE_IDS
            ):
                return self._fail_contract_error(
                    review,
                    code=EngineErrorCode.MALFORMED_REVIEW_REQUEST.value,
                    message=f"ERC container node_logical_id is not submittable: '{node_logical_id}'",
                )
            applicable_rules = self._resolve_reviewer_policy_rules(
                call_definition=call_definition,
                node_logical_id=node_logical_id,
                review_stage=review_stage,
            )
            applicable_policy_by_node[node_logical_id] = applicable_rules

            expectations = self.repository.get_expectations_for_node(node.id)
            assessable, not_assessable = self._partition_expectations(
                node_logical_id=node_logical_id,
                expectations=expectations,
                submitted_text_by_node=submitted_text_by_node,
            )

            for expectation, reason in not_assessable:
                not_assessable_payloads.append(
                    (
                        expectation.id,
                        ReviewRating.NOTE,
                        "Not assessable due to missing cross-node context.",
                        AssessmentStatus.NOT_ASSESSABLE,
                        reason,
                    )
                )

            for expectation in assessable:
                expectation_id = str(expectation.id)
                expectation_payload: dict[str, object] = {
                    "expectation_id": expectation_id,
                    "node_logical_id": node_logical_id,
                }
                if expectation.expectation_strength.value == "MANDATORY":
                    expectation_payload["required"] = True
                request_expectations.append(
                    expectation_payload
                )
                expectation_map[expectation_id] = expectation

        call_config_snapshot = {
            "schema_version": "v1",
            "expectations": request_expectations,
        }
        canonical_snapshot = canonicalize_for_digest(call_config_snapshot)
        computed_digest = "sha256:" + hashlib.sha256(
            canonical_snapshot.encode("utf-8")
        ).hexdigest()
        payload = {
            "request_id": str(review.id),
            "mode": "DIAGNOSTIC",
            "stage_ref": review_stage,
            "call_config_snapshot": call_config_snapshot,
            "call_config_digest": call_config_digest_override or computed_digest,
            "proposal_nodes": submitted_text_by_node,
        }

        try:
            review_request = validate_review_request_payload(payload)
            result = (
                run_review_pipeline(review_request)
                if request_expectations
                else PipelineResult(
                    request_id=str(review.id),
                    pipeline_status="SUCCESS",
                    failure_code=None,
                    diagnostics=[],
                    compatibility_output={},
                    findings=[],
                    review_cards=[],
                    telemetry={},
                )
            )
        except ReviewRequestValidationError as err:
            return self._fail_contract_error(review, code=err.code, message=err.message)
        except EngineContractError as err:
            return self._fail_contract_error(
                review,
                code=err.code.value,
                message=err.message,
            )
        except TimeoutError as err:
            return self._fail_execution_error(
                review,
                code=EngineErrorCode.TIMEOUT.value,
                message=str(err),
            )
        except Exception as err:
            return self._fail_execution_error(
                review,
                code=EngineErrorCode.ENGINE_EXECUTION_FAILED.value,
                message=str(err),
            )

        unresolved = [
            card.expectation_id
            for card in result.review_cards
            if card.expectation_id not in expectation_map
        ]
        if unresolved:
            return self._fail_contract_error(
                review,
                code=EngineErrorCode.EXPECTATION_REF_UNRESOLVABLE.value,
                message=f"Unresolvable expectation ref: {sorted(set(unresolved))[0]}",
            )

        feedback_texts_by_node: dict[str, list[str]] = {}
        for card in result.review_cards:
            feedback_texts_by_node.setdefault(card.node_logical_id, []).append(card.feedback)

        blocking_policy_violations: list[str] = []
        warning_policy_violations: list[str] = []
        for node_logical_id, node_feedbacks in feedback_texts_by_node.items():
            applicable_rules = applicable_policy_by_node.get(node_logical_id, [])
            blocking, warning = find_policy_violations(
                feedback_texts=node_feedbacks,
                policy_rules=applicable_rules,
            )
            blocking_policy_violations.extend(blocking)
            warning_policy_violations.extend(warning)
        if blocking_policy_violations:
            review.status = ReviewStatus.FAILED
            review.overall_summary = (
                f"{STRUCTURED_POLICY_BLOCKING_PREFIX} "
                + "; ".join(blocking_policy_violations)
            )
            self.repository.update_review(review)
            return review, []

        card_payloads: list[
            tuple[UUID, ReviewRating, str, AssessmentStatus, str | None]
        ] = list(not_assessable_payloads)
        for card in result.review_cards:
            expectation = expectation_map[card.expectation_id]
            feedback_text = self._resolve_feedback_text_for_card(
                call_code=call.code,
                node_logical_id=card.node_logical_id,
                expectation=expectation,
                feedback_text=card.feedback,
            )
            card_payloads.append(
                (
                    expectation.id,
                    ReviewRating[card.rating],
                    feedback_text,
                    AssessmentStatus.ASSESSED,
                    None,
                )
            )

        cards = self.repository.create_review_cards_batch(
            review_id=review.id,
            cards=card_payloads,
        )

        review.status = ReviewStatus.COMPLETED
        review.overall_summary = (
            f"{STRUCTURED_SUMMARY_COMPLETED_PREFIX} {len(cards)} findings via pipeline_v1."
        )
        if warning_policy_violations:
            review.overall_summary += (
                f" {STRUCTURED_POLICY_WARNING_PREFIX} "
                + "; ".join(warning_policy_violations)
            )
        review.overall_rating = ReviewRating.NOTE
        self.repository.update_review(review)
        return review, cards

    def _fail_contract_error(
        self,
        review: Review,
        *,
        code: str,
        message: str,
    ) -> tuple[Review, list[ReviewCard]]:
        review.status = ReviewStatus.FAILED
        review.overall_summary = f"{code}: {message}"
        self.repository.update_review(review)
        return review, []

    def _fail_execution_error(
        self,
        review: Review,
        *,
        code: str,
        message: str,
    ) -> tuple[Review, list[ReviewCard]]:
        normalized_message = message.strip()
        if code == EngineErrorCode.TIMEOUT.value and not normalized_message:
            normalized_message = (
                f"Structured review execution timed out after {self._timeout_seconds:.2f}s."
            )
        review.status = ReviewStatus.FAILED
        review.overall_summary = f"{code}: {normalized_message}"
        self.repository.update_review(review)
        return review, []

    def _needs_alignment_context(
        self,
        node_logical_id: str,
        expectation: NodeExpectation,
    ) -> bool:
        if node_logical_id != "research_idea":
            return False
        element_logical_id = expectation.element.logical_id if expectation.element else None
        return element_logical_id in ALIGNMENT_ELEMENT_IDS

    def _resolve_reviewer_policy_rules(
        self,
        *,
        call_definition,
        node_logical_id: str,
        review_stage: ReviewStage,
    ) -> list[ReviewerPolicyRule]:
        return get_applicable_reviewer_policy_rules(
            call_definition=call_definition,
            node_logical_id=node_logical_id,
            review_stage=review_stage,
        )

    def _resolve_feedback_text_for_card(
        self,
        *,
        call_code: str,
        node_logical_id: str,
        expectation: NodeExpectation,
        feedback_text: str,
    ) -> str:
        if (
            feedback_text != "content_evaluated"
            or call_code not in WF0069_ACTIONABILITY_CALL_CODES
        ):
            return feedback_text

        # Keep the remediation scoped to the locked call wedge at the service seam.
        # Evaluator/mapper are call-agnostic and would widen behavior across unrelated calls.
        element_label = self._normalize_expectation_element_label(expectation)
        return (
            f"Revise {node_logical_id} to explicitly strengthen {element_label} "
            "with concrete evidence and outcomes."
        )

    @staticmethod
    def _normalize_expectation_element_label(expectation: NodeExpectation) -> str:
        if expectation.element is None:
            return "this evaluation element"
        if expectation.element.name:
            return expectation.element.name.strip().lower()
        if expectation.element.logical_id:
            return expectation.element.logical_id.replace("_", " ").strip().lower()
        return "this evaluation element"
