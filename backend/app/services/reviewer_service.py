"""
Reviewer service - business logic layer.

Rule: Services call Repositories. Controllers call Services.
"""

from uuid import UUID

from app.models.domain import NodeExpectation, Review, ReviewCard
from app.repositories.review_repository import ReviewRepository


class ReviewerService:
    """Service for generating reviews from proposal snippets."""

    def __init__(self, repository: ReviewRepository) -> None:
        self.repository = repository

    def generate_review(
        self,
        node_id: UUID,
        snippet_text: str,
        call_id: UUID,
    ) -> tuple[Review, list[ReviewCard]]:
        """
        Generate a review for a proposal snippet.

        1. Fetch NodeExpectations for the node
        2. Reject if zero expectations (AD 2.1)
        3. Get active prompt template
        4. Create anonymous user + snippet
        5. Generate mock AI feedback
        6. Create Review + ReviewCards

        Returns:
            Tuple of (Review, list[ReviewCard])

        Raises:
            ValueError: If node has no expectations or no active template

        """
        # 1. Fetch expectations
        expectations = self.repository.get_expectations_for_node(node_id)

        # 2. AD 2.1: Reject if zero expectations
        if not expectations:
            raise ValueError("No evaluation criteria defined for this section.")

        # 3. Get active prompt template
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

        # 6. Create review
        review = self.repository.create_review(
            snippet_id=snippet.id,
            template_id=template.id,
        )

        # 7. Generate mock feedback and create cards
        cards = []
        for expectation in expectations:
            feedback = self._generate_mock_feedback(expectation, snippet_text)
            card = self.repository.create_review_card(
                review_id=review.id,
                expectation_id=expectation.id,
                feedback=feedback,
            )
            cards.append(card)

        return review, cards

    def _generate_mock_feedback(
        self,
        expectation: NodeExpectation,
        snippet_text: str,
    ) -> str:
        """
        Generate mock AI feedback for prototype.

        In production, this would call the AI API with the assembled prompt.
        """
        # Mock feedback based on expectation strength
        strength_feedback = {
            "MANDATORY": "This is a MANDATORY criterion. ",
            "IMPORTANT": "This is an IMPORTANT criterion. ",
            "OPTIONAL": "This is an OPTIONAL criterion. ",
        }

        intent_feedback = {
            "COMPLIANCE": "Compliance check: ",
            "QUALITY": "Quality assessment: ",
            "RISK": "Risk identification: ",
            "STRATEGIC_FIT": "Strategic fit evaluation: ",
        }

        prefix = strength_feedback.get(expectation.expectation_strength.value, "")
        intent = intent_feedback.get(expectation.evaluation_intent.value, "")

        return (
            f"{prefix}{intent}"
            f"[MOCK] Feedback for '{expectation.element.name if expectation.element else 'unknown'}': "
            f"The submitted text ({len(snippet_text)} chars) has been reviewed against: "
            f"'{expectation.guidance_note or 'No specific guidance'}'"
        )
