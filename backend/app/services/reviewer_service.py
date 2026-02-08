"""
Reviewer service - business logic layer.

Rule: Services call Repositories. Controllers call Services.
"""

import json
import logging
from uuid import UUID

from pydantic import ValidationError

from app.models.domain import (
    NodeExpectation,
    Review,
    ReviewCard,
    ReviewRating,
    ReviewStatus,
)
from app.repositories.review_repository import ReviewRepository
from app.schemas.llm_response import LLMReviewResponse
from app.services.llm_client import LLMClientError, OpenAIClient
from app.services.prompt_builder import build_review_prompt

logger = logging.getLogger(__name__)


class ReviewerService:
    """Service for generating reviews from proposal snippets."""

    def __init__(
        self,
        repository: ReviewRepository,
        llm_client: OpenAIClient | None = None,
    ) -> None:
        self.repository = repository
        self._llm_client = llm_client

    @property
    def llm_client(self) -> OpenAIClient:
        """Lazy-load LLM client."""
        if self._llm_client is None:
            self._llm_client = OpenAIClient()
        return self._llm_client

    def generate_review(
        self,
        node_id: UUID,
        snippet_text: str,
        call_id: UUID,
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
        # 1. Fetch expectations
        expectations = self.repository.get_expectations_for_node(node_id)

        # 2. AD 2.1: Reject if zero expectations
        if not expectations:
            raise ValueError("No evaluation criteria defined for this section.")

        # 3. Get active prompt template (for audit trail)
        template = self.repository.get_active_prompt_template()
        if not template:
            raise ValueError("No active prompt template found.")

        # 4. Get node for context
        node = self.repository.get_node_by_id(node_id)
        if not node:
            msg = f"Node {node_id} not found."
            raise ValueError(msg)

        # 5. Create user and snippet
        user = self.repository.create_user()
        snippet = self.repository.create_snippet(
            user_id=user.id,
            call_id=call_id,
            node_id=node_id,
            text=snippet_text,
        )

        # 6. Build prompt
        prompt = build_review_prompt(node, snippet_text, expectations)

        # 7. Create review record (status=PENDING initially)
        review = self.repository.create_review(
            snippet_id=snippet.id,
            template_id=template.id,
        )

        # Store prompt and model info
        review.prompt_sent = prompt
        review.llm_model = self.llm_client.get_model_name()

        # 8. Call LLM
        try:
            raw_response = self.llm_client.generate(prompt)
            review.raw_llm_response = raw_response
        except LLMClientError as e:
            logger.error(f"LLM call failed: {e}")
            review.status = ReviewStatus.FAILED
            review.overall_summary = f"LLM call failed: {e}"
            self.repository.update_review(review)
            raise ValueError(f"LLM call failed: {e}") from e

        # 9. Parse and validate response
        try:
            llm_response = self._parse_llm_response(raw_response)
            self._validate_response(llm_response, expectations)
        except ValueError as e:
            logger.error(f"LLM response validation failed: {e}")
            review.status = ReviewStatus.FAILED
            review.overall_summary = f"Response validation failed: {e}"
            self.repository.update_review(review)
            raise

        # 10. Create ReviewCards
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

        # 11. Finalize review as COMPLETED
        review.status = ReviewStatus.COMPLETED
        review.overall_rating = ReviewRating.NOTE  # Defer rating logic
        review.overall_summary = (
            f"Review completed with {len(cards)} findings."
        )
        self.repository.update_review(review)

        logger.info(f"Review {review.id} completed with {len(cards)} cards")
        return review, cards

    def _parse_llm_response(self, raw_response: str) -> LLMReviewResponse:
        """Parse raw LLM response into structured format."""
        try:
            data = json.loads(raw_response)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON from LLM: {e}") from e

        try:
            return LLMReviewResponse.model_validate(data)
        except ValidationError as e:
            raise ValueError(f"LLM response schema validation failed: {e}") from e

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
