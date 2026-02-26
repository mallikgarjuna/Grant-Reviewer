"""
Reviewer service - business logic layer.

Rule: Services call Repositories. Controllers call Services.
"""

import logging
import os
from datetime import datetime
from uuid import UUID

from app.models.domain import (
    Review,
    ReviewCard,
    ReviewRating,
    ReviewStatus,
)
from app.repositories.review_repository import ReviewRepository
from app.services.llm_client import LLMClientProtocol, OpenAIClient
from app.services.review_execution_core import (
    ExecutionFailureCategory,
    ReviewExecutionCore,
)
from app.services.reviewer_policy import (
    get_applicable_reviewer_policy_rules,
    ReviewStage,
)

logger = logging.getLogger(__name__)


class ReviewerService:
    """Service for generating reviews from proposal snippets."""

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
        logger.debug("ReviewerService initialized")

    @property
    def llm_client(self) -> LLMClientProtocol:
        """Lazy-load LLM client."""
        if self._llm_client is None:
            logger.debug("Lazy-loading OpenAI client...")
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

    def generate_review(
        self,
        node_id: UUID,
        snippet_text: str,
        call_id: UUID,
        review_stage: ReviewStage,
        external_user_id: str,
        *,
        idempotency_key: str | None = None,
        request_payload_sha256: str | None = None,
        idempotency_expires_at: datetime | None = None,
    ) -> tuple[Review, list[ReviewCard]]:
        """
        Generate a review for a proposal snippet using LLM.

        Flow:
        1. Fetch NodeExpectations for the node
        2. Reject if zero expectations (AD 2.1)
        3. Get active prompt template (for template_id tracking)
        4. Create anonymous user + snippet
        5. Build prompt and call LLM
        6. Parse and validate response
        7. Create Review + ReviewCards atomically

        Returns:
            Tuple of (Review, list[ReviewCard])

        Raises:
            ValueError: If node has no expectations or validation fails
        """
        logger.info(f"[Review] Starting review for node {node_id}")

        # 1. Fetch expectations
        logger.debug(f"[Review] Fetching expectations for node {node_id}")
        expectations = self.repository.get_expectations_for_node(node_id)
        logger.info(f"[Review] Found {len(expectations)} expectations")

        # 2. AD 2.1: Reject if zero expectations
        if not expectations:
            logger.warning(f"[Review] No expectations for node {node_id}, rejecting")
            raise ValueError("No evaluation criteria defined for this section.")

        # 3. Get active prompt template (for audit trail)
        template = self.repository.get_active_prompt_template()
        if not template:
            logger.error("[Review] No active prompt template found")
            raise ValueError("No active prompt template found.")
        logger.debug(f"[Review] Using template: {template.id}")

        # 4. Get node for context
        node = self.repository.get_node_by_id(node_id)
        if not node:
            logger.error(f"[Review] Node {node_id} not found")
            msg = f"Node {node_id} not found."
            raise ValueError(msg)
        logger.debug(f"[Review] Node title: {node.title}")
        call_definition = self.repository.get_call_definition_by_call_id(call_id)
        reviewer_policy_rules = get_applicable_reviewer_policy_rules(
            call_definition=call_definition,
            node_logical_id=node.logical_id,
            review_stage=review_stage,
        )
        logger.debug(
            "[Review] Reviewer policy rules applied: %s",
            len(reviewer_policy_rules),
        )

        # 5. Create/fetch user and create snippet
        logger.debug("[Review] Creating user and snippet...")
        user = self.repository.get_or_create_user_by_external_user_id(external_user_id)
        snippet = self.repository.create_snippet(
            user_id=user.id,
            call_id=call_id,
            node_id=node_id,
            text=snippet_text,
        )
        logger.debug(
            f"[Review] Created snippet {snippet.id} ({len(snippet_text)} chars)"
        )

        # 7. Create review record (status=PENDING initially)
        review = self.repository.create_review(
            snippet_id=snippet.id,
            template_id=template.id,
            external_user_id=external_user_id,
            idempotency_key=idempotency_key,
            request_payload_sha256=request_payload_sha256,
            idempotency_expires_at=idempotency_expires_at,
        )
        logger.info(f"[Review] Created review {review.id} (status=PENDING)")

        # Store model info
        review.llm_model = self.llm_client.get_model_name()
        node_result = self.execution_core.execute_assessable_node(
            node=node,
            snippet_text=snippet_text,
            expectations=expectations,
            reviewer_policy_rules=reviewer_policy_rules,
        )
        review.prompt_sent = node_result.prompt
        review.raw_llm_response = node_result.raw_response
        if node_result.failure is not None:
            review.status = ReviewStatus.FAILED
            review.overall_summary = self._failure_summary(
                category=node_result.failure.category,
                message=node_result.failure.message,
            )
            self.repository.update_review(review)
            return review, []

        if node_result.warning_violations:
            logger.warning(
                "[Review] Reviewer-policy warning violations: %s",
                node_result.warning_violations,
            )

        # 10. Create ReviewCards
        logger.debug("[Review] Creating ReviewCards...")
        cards = []
        expectation_map = {str(exp.id): exp for exp in expectations}

        for feedback_item in node_result.feedbacks:
            expectation = expectation_map[feedback_item.node_expectation_id]
            card = self.repository.create_review_card(
                review_id=review.id,
                expectation_id=expectation.id,
                rating=ReviewRating.NOTE,  # Defer rating to Phase 2
                feedback=feedback_item.feedback,
            )
            cards.append(card)
        logger.debug(f"[Review] Created {len(cards)} ReviewCards")

        # 11. Finalize review as COMPLETED
        review.status = ReviewStatus.COMPLETED
        review.overall_rating = ReviewRating.NOTE  # Defer rating logic
        review.overall_summary = f"Review completed with {len(cards)} findings."
        if node_result.warning_violations:
            review.overall_summary += (
                " Reviewer-policy warnings: "
                + "; ".join(node_result.warning_violations)
            )
        self.repository.update_review(review)

        logger.info(f"[Review] ✓ Review {review.id} COMPLETED with {len(cards)} cards")
        return review, cards

    def _failure_summary(
        self,
        *,
        category: ExecutionFailureCategory,
        message: str,
    ) -> str:
        if category == ExecutionFailureCategory.TIMEOUT:
            return message
        if category == ExecutionFailureCategory.LLM_FAILURE:
            return f"LLM call failed: {message}"
        if category == ExecutionFailureCategory.POLICY_BLOCKING:
            return "Reviewer-policy blocking violations detected: " + message
        return f"Response validation failed: {message}"
