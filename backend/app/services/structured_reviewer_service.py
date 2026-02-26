"""Structured review service for multi-node proposal assessments."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from uuid import UUID

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
from app.services.review_execution_core import (
    ReviewExecutionCore,
    format_execution_failure_summary,
)
from app.services.reviewer_policy import (
    ReviewStage,
    get_applicable_reviewer_policy_rules,
)

logger = logging.getLogger(__name__)

ALIGNMENT_ELEMENT_IDS = {
    "elem_cv_idea_alignment",
    "elem_alignment_plan_credibility",
}
ALIGNMENT_REQUIRED_NODES = ("academic_profile", "key_outputs")


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

    def generate_structured_review(
        self,
        *,
        review_stage: ReviewStage,
        call_id: UUID,
        nodes: list[tuple[str, str]],
        external_user_id: str,
        idempotency_key: str | None = None,
        request_payload_sha256: str | None = None,
        idempotency_expires_at: datetime | None = None,
    ) -> tuple[Review, list[ReviewCard]]:
        """Generate one structured review for one call across multiple nodes."""
        if not nodes:
            raise ValueError("At least one node is required.")

        template = self.repository.get_active_prompt_template()
        if template is None:
            raise ValueError("No active prompt template found.")

        call_nodes = self.repository.get_nodes_for_call(call_id)
        node_by_logical_id = {
            node.logical_id: node
            for node, _ in call_nodes
            if isinstance(node.logical_id, str) and node.logical_id
        }
        submitted_text_by_node = {node_logical_id: text for node_logical_id, text in nodes}
        call = self.repository.get_call_by_id(call_id)
        if call is None:
            raise ValueError("Funding call not found.")
        call_definition = self.repository.get_call_definition_by_call_id(call_id)
        structured_payload = {
            "call_id": str(call_id),
            "call_name": call.name,
            "review_stage": review_stage,
            "nodes": submitted_text_by_node,
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
        review.llm_model = self.llm_client.get_model_name()
        self.repository.update_review(review)

        all_cards: list[ReviewCard] = []
        prompt_logs: list[dict[str, str]] = []
        raw_logs: list[dict[str, str]] = []

        for node_logical_id, node_text in nodes:
            node = node_by_logical_id.get(node_logical_id)
            if node is None:
                raise ValueError(f"Unknown node_logical_id: '{node_logical_id}'")

            expectations = self.repository.get_expectations_for_node(node.id)
            if not expectations:
                logger.warning(
                    "[StructuredReview] Node %s has zero expectations",
                    node_logical_id,
                )
                continue

            assessable, not_assessable = self._partition_expectations(
                node_logical_id=node_logical_id,
                expectations=expectations,
                submitted_text_by_node=submitted_text_by_node,
            )

            # Persist deterministic NOT_ASSESSABLE cards first for explicit traceability.
            for expectation, reason in not_assessable:
                card = self.repository.create_review_card(
                    review_id=review.id,
                    expectation_id=expectation.id,
                    # MVP: keep deterministic card severity neutral while typed status
                    # communicates assessability.
                    rating=ReviewRating.NOTE,
                    feedback="Not assessable due to missing cross-node context.",
                    assessment_status=AssessmentStatus.NOT_ASSESSABLE,
                    not_assessable_reason=reason,
                )
                all_cards.append(card)

            if not assessable:
                continue

            cross_context = self._build_cross_node_context(
                node_logical_id=node_logical_id,
                expectations=assessable,
                submitted_text_by_node=submitted_text_by_node,
            )
            reviewer_policy_rules = get_applicable_reviewer_policy_rules(
                call_definition=call_definition,
                node_logical_id=node.logical_id,
                review_stage=review_stage,
            )
            node_result = self.execution_core.execute_assessable_node(
                node=node,
                snippet_text=node_text,
                expectations=assessable,
                reviewer_policy_rules=reviewer_policy_rules,
                cross_node_context=cross_context,
            )
            prompt_logs.append(
                {"node_logical_id": node_logical_id, "prompt": node_result.prompt}
            )
            if node_result.raw_response is not None:
                raw_logs.append(
                    {"node_logical_id": node_logical_id, "raw": node_result.raw_response}
                )

            if node_result.failure is not None:
                review.status = ReviewStatus.FAILED
                review.overall_summary = format_execution_failure_summary(
                    flow="structured",
                    category=node_result.failure.category,
                    message=node_result.failure.message,
                    timeout_seconds=self._timeout_seconds,
                    node_logical_id=node_logical_id,
                )
                review.prompt_sent = json.dumps(prompt_logs)
                review.raw_llm_response = json.dumps(raw_logs)
                self.repository.update_review(review)
                return review, all_cards

            if node_result.warning_violations:
                logger.warning(
                    "[StructuredReview] Reviewer-policy warnings for %s: %s",
                    node_logical_id,
                    node_result.warning_violations,
                )

            expectation_map = {str(expectation.id): expectation for expectation in assessable}
            for feedback_item in node_result.feedbacks:
                expectation = expectation_map[feedback_item.node_expectation_id]
                card = self.repository.create_review_card(
                    review_id=review.id,
                    expectation_id=expectation.id,
                    # MVP: severity mapping remains NOTE-only for structured reviews.
                    rating=ReviewRating.NOTE,
                    feedback=feedback_item.feedback,
                    assessment_status=AssessmentStatus.ASSESSED,
                )
                all_cards.append(card)

        review.status = ReviewStatus.COMPLETED
        review.overall_rating = ReviewRating.NOTE
        review.overall_summary = (
            f"Structured review completed with {len(all_cards)} findings."
        )
        review.prompt_sent = json.dumps(prompt_logs)
        review.raw_llm_response = json.dumps(raw_logs)
        self.repository.update_review(review)
        return review, all_cards

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

    def _build_cross_node_context(
        self,
        *,
        node_logical_id: str,
        expectations: list[NodeExpectation],
        submitted_text_by_node: dict[str, str],
    ) -> dict[str, str] | None:
        if not any(
            self._needs_alignment_context(node_logical_id, expectation)
            for expectation in expectations
        ):
            return None

        context: dict[str, str] = {}
        for upstream_node in ALIGNMENT_REQUIRED_NODES:
            upstream_text = submitted_text_by_node.get(upstream_node, "").strip()
            if upstream_text:
                context[upstream_node] = upstream_text

        return context or None

    def _needs_alignment_context(
        self,
        node_logical_id: str,
        expectation: NodeExpectation,
    ) -> bool:
        if node_logical_id != "research_idea":
            return False
        element_logical_id = expectation.element.logical_id if expectation.element else None
        return element_logical_id in ALIGNMENT_ELEMENT_IDS
