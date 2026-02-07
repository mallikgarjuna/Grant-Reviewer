"""
Review repository - database access layer.

Rule: Only repositories talk to the database directly.
"""

from uuid import UUID

from sqlmodel import Session, select

from app.models.domain import (
    NodeExpectation,
    PromptTemplate,
    ProposalNode,
    ProposalSnippet,
    Review,
    ReviewCard,
    User,
)


class ReviewRepository:
    """Repository for review-related database operations."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_node_by_id(self, node_id: UUID) -> ProposalNode | None:
        """Fetch a proposal node by ID."""
        return self.session.get(ProposalNode, node_id)

    def get_expectations_for_node(self, node_id: UUID) -> list[NodeExpectation]:
        """Fetch all NodeExpectations for a given proposal node, ordered."""
        statement = (
            select(NodeExpectation)
            .where(NodeExpectation.proposal_node_id == node_id)
            .order_by(NodeExpectation.order_index)
        )
        return list(self.session.exec(statement).all())

    def get_active_prompt_template(self) -> PromptTemplate | None:
        """Fetch the currently active prompt template."""
        statement = select(PromptTemplate).where(PromptTemplate.is_active)
        return self.session.exec(statement).first()

    def create_user(self, *, is_anonymous: bool = True) -> User:
        """Create a new user."""
        user = User(is_anonymous=is_anonymous)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def create_snippet(
        self,
        user_id: UUID,
        call_id: UUID,
        node_id: UUID,
        text: str,
    ) -> ProposalSnippet:
        """Create a new proposal snippet."""
        snippet = ProposalSnippet(
            user_id=user_id,
            funding_call_id=call_id,
            proposal_node_id=node_id,
            pasted_text=text,
        )
        self.session.add(snippet)
        self.session.commit()
        self.session.refresh(snippet)
        return snippet

    def create_review(
        self,
        snippet_id: UUID,
        template_id: UUID,
    ) -> Review:
        """Create a new review record."""
        review = Review(
            proposal_snippet_id=snippet_id,
            prompt_template_id=template_id,
        )
        self.session.add(review)
        self.session.commit()
        self.session.refresh(review)
        return review

    def create_review_card(
        self,
        review_id: UUID,
        expectation_id: UUID,
        feedback: str,
    ) -> ReviewCard:
        """Create a new review card."""
        card = ReviewCard(
            review_id=review_id,
            node_expectation_id=expectation_id,
            feedback_text=feedback,
        )
        self.session.add(card)
        self.session.commit()
        self.session.refresh(card)
        return card
