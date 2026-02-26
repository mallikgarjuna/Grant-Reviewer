"""
Reviewer service - business logic layer.

Rule: Services call Repositories. Controllers call Services.
"""

import logging
import os
from concurrent.futures import TimeoutError
from datetime import datetime
from uuid import UUID

from app.models.domain import (
    NodeExpectation,
    Review,
    ReviewCard,
    ReviewRating,
    ReviewStatus,
)
from app.repositories.review_repository import ReviewRepository
from app.schemas.llm_response import LLMReviewResponse
from app.services.llm_client import LLMClientError, LLMClientProtocol, OpenAIClient
from app.services.llm_helpers import generate_with_timeout, parse_llm_response
from app.services.prompt_builder import build_review_prompt
from app.services.reviewer_policy import (
    find_policy_violations,
    get_applicable_reviewer_policy_rules,
    infer_review_stage,
)

logger = logging.getLogger(__name__)


class ReviewerService:
    """Service for generating reviews from proposal snippets."""

    def __init__(
        self,
        repository: ReviewRepository,
        llm_client: LLMClientProtocol | None = None,
    ) -> None:
        self.repository = repository
        self._llm_client = llm_client
        self._timeout_seconds = float(os.getenv("REVIEW_TIMEOUT_SECONDS", "30"))
        logger.debug("ReviewerService initialized")

    @property
    def llm_client(self) -> LLMClientProtocol:
        """Lazy-load LLM client."""
        if self._llm_client is None:
            logger.debug("Lazy-loading OpenAI client...")
            self._llm_client = OpenAIClient()
        return self._llm_client

    def generate_review(
        self,
        node_id: UUID,
        snippet_text: str,
        call_id: UUID,
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
        review_stage = infer_review_stage(node.logical_id)
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

        # 6. Build prompt
        logger.debug("[Review] Building prompt...")
        prompt = build_review_prompt(
            node,
            snippet_text,
            expectations,
            reviewer_policy_rules=reviewer_policy_rules,
        )
        logger.debug(f"[Review] Prompt built ({len(prompt)} chars)")

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

        # Store prompt and model info
        review.prompt_sent = prompt
        review.llm_model = self.llm_client.get_model_name()

        # 8. Call LLM
        try:
            logger.info("[Review] Calling LLM...")
            raw_response = generate_with_timeout(
                llm_client=self.llm_client,
                prompt=prompt,
                timeout_seconds=self._timeout_seconds,
            )
            review.raw_llm_response = raw_response
            logger.info("[Review] LLM call successful")
        except TimeoutError:
            logger.error(
                "[Review] LLM call timed out after %.2fs", self._timeout_seconds
            )
            review.status = ReviewStatus.FAILED
            review.overall_summary = (
                f"LLM call timed out after {self._timeout_seconds:.2f}s."
            )
            self.repository.update_review(review)
            return review, []
        except LLMClientError as e:
            logger.error(f"[Review] LLM call failed: {e}")
            review.status = ReviewStatus.FAILED
            review.overall_summary = f"LLM call failed: {e}"
            self.repository.update_review(review)
            return review, []

        # 9. Parse and validate response
        try:
            logger.debug("[Review] Parsing LLM response...")
            llm_response = parse_llm_response(raw_response)
            logger.debug(
                f"[Review] Parsed {len(llm_response.feedbacks)} feedback items"
            )

            logger.debug("[Review] Validating response...")
            self._validate_response(llm_response, expectations)
            logger.info("[Review] Response validation passed")
        except ValueError as e:
            logger.error(f"[Review] Response validation failed: {e}")
            review.status = ReviewStatus.FAILED
            review.overall_summary = f"Response validation failed: {e}"
            self.repository.update_review(review)
            return review, []

        blocking_violations, warning_violations = find_policy_violations(
            feedback_texts=[item.feedback for item in llm_response.feedbacks],
            policy_rules=reviewer_policy_rules,
        )
        if blocking_violations:
            logger.error(
                "[Review] Blocking reviewer-policy violations: %s",
                blocking_violations,
            )
            review.status = ReviewStatus.FAILED
            review.overall_summary = (
                "Reviewer-policy blocking violations detected: "
                + "; ".join(blocking_violations)
            )
            self.repository.update_review(review)
            return review, []
        if warning_violations:
            logger.warning(
                "[Review] Reviewer-policy warning violations: %s",
                warning_violations,
            )

        # 10. Create ReviewCards
        logger.debug("[Review] Creating ReviewCards...")
        cards = []
        expectation_map = {str(exp.id): exp for exp in expectations}

        for feedback_item in llm_response.feedbacks:
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
        if warning_violations:
            review.overall_summary += (
                " Reviewer-policy warnings: " + "; ".join(warning_violations)
            )
        self.repository.update_review(review)

        logger.info(f"[Review] ✓ Review {review.id} COMPLETED with {len(cards)} cards")
        return review, cards

    def _validate_response(
        self,
        response: LLMReviewResponse,
        expectations: list[NodeExpectation],
    ) -> None:
        """Validate LLM response matches expectations."""
        # Check cardinality
        expected_count = len(expectations)
        actual_count = len(response.feedbacks)
        if actual_count != expected_count:
            raise ValueError(
                f"Cardinality mismatch: expected {expected_count} feedbacks, "
                f"got {actual_count}"
            )

        # Check all expectation IDs exist and belong to this node
        valid_ids = {str(exp.id) for exp in expectations}
        received_ids = {fb.node_expectation_id for fb in response.feedbacks}

        missing = valid_ids - received_ids
        if missing:
            raise ValueError(f"Missing feedback for expectations: {missing}")

        extra = received_ids - valid_ids
        if extra:
            raise ValueError(f"Unknown expectation IDs in response: {extra}")
