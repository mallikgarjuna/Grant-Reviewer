"""Structured review service for multi-node proposal assessments."""

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


def _normalize_submitted_nodes(
    nodes: list[tuple[str, str]],
) -> tuple[list[str], dict[str, str]]:
    submitted_node_logical_ids: list[str] = []
    submitted_text_by_node: dict[str, str] = {}
    for node_logical_id, text in nodes:
        submitted_node_logical_ids.append(node_logical_id)
        submitted_text_by_node[node_logical_id] = text
    return submitted_node_logical_ids, submitted_text_by_node


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

        call_nodes = self.repository.get_nodes_for_call(call_id)
        node_by_logical_id = {
            node.logical_id: node
            for node, _ in call_nodes
            if isinstance(node.logical_id, str) and node.logical_id
        }
        submitted_node_logical_ids, submitted_text_by_node = _normalize_submitted_nodes(
            nodes
        )
        structured_payload = {
            "call_id": str(call_id),
            "call_name": call.name,
            "review_stage": review_stage,
            "nodes": submitted_text_by_node,
            "submitted_node_logical_ids": submitted_node_logical_ids,
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
        prompt_policy_by_node: dict[str, list[dict[str, str]]] = {}
        applicable_policy_by_node: dict[str, list[ReviewerPolicyRule]] = {}
        for node_logical_id, _ in nodes:
            node = node_by_logical_id.get(node_logical_id)
            if node is None:
                return self._fail_contract_error(
                    review,
                    code=EngineErrorCode.MALFORMED_REVIEW_REQUEST.value,
                    message=f"Unknown node_logical_id: '{node_logical_id}'",
                )
            applicable_rules = self._resolve_reviewer_policy_rules(
                call_definition=call_definition,
                node_logical_id=node_logical_id,
                review_stage=review_stage,
            )
            applicable_policy_by_node[node_logical_id] = applicable_rules
            prompt_policy = self._build_prompt_policy_payload(applicable_rules)
            if prompt_policy:
                prompt_policy_by_node[node_logical_id] = prompt_policy

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
                request_expectations.append(
                    {
                        "expectation_id": expectation_id,
                        "node_logical_id": node_logical_id,
                        "check_id": "check.presence",
                        "required": expectation.expectation_strength.value == "MANDATORY",
                        "reviewer_policy_prompt_rules": prompt_policy,
                    }
                )
                expectation_map[expectation_id] = expectation

        call_config_snapshot = {
            "expectations": request_expectations,
            "reviewer_policy_prompt_by_node": prompt_policy_by_node,
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
            card_payloads.append(
                (
                    expectation.id,
                    ReviewRating[card.rating],
                    card.feedback,
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

    def _build_prompt_policy_payload(
        self,
        rules: list[ReviewerPolicyRule],
    ) -> list[dict[str, str]]:
        return [
            {
                "id": rule.id,
                "rule_type": rule.rule_type,
                "instruction": rule.instruction,
                "severity": rule.severity,
            }
            for rule in rules
            if rule.enforcement_mode == "PROMPT_ONLY"
        ]
