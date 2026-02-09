"""
Review repository - database access layer.

Rule: Only repositories talk to the database directly.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import func
from sqlmodel import Session, select

from app.models.domain import (
    FundingAgency,
    FundingCall,
    NodeExpectation,
    PromptTemplate,
    ProposalNode,
    ProposalSnippet,
    Review,
    ReviewCard,
    ReviewRating,
    User,
)


class ReviewRepository:
    """Repository for review-related database operations."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_node_by_id(self, node_id: UUID) -> ProposalNode | None:
        """Fetch a proposal node by ID."""
        return self.session.get(ProposalNode, node_id)

    def get_call_by_id(self, call_id: UUID) -> FundingCall | None:
        """Fetch a funding call by ID."""
        return self.session.get(FundingCall, call_id)

    def get_active_calls(self) -> list[tuple[FundingCall, FundingAgency]]:
        """Fetch active calls with their agencies."""
        statement = (
            select(FundingCall, FundingAgency)
            .join(FundingAgency, FundingCall.funding_agency_id == FundingAgency.id)
            .where(FundingCall.is_active)
            .order_by(FundingCall.call_year.desc(), FundingCall.code)
        )
        return list(self.session.exec(statement).all())

    def get_nodes_for_call(
        self,
        call_id: UUID,
    ) -> list[tuple[ProposalNode, bool]]:
        """Fetch call nodes and whether they currently have expectations."""
        statement = (
            select(ProposalNode)
            .where(ProposalNode.funding_call_id == call_id)
            .order_by(ProposalNode.order_index, ProposalNode.title)
        )
        nodes = list(self.session.exec(statement).all())
        if not nodes:
            return []

        node_ids = [node.id for node in nodes]
        expectation_statement = (
            select(NodeExpectation.proposal_node_id, func.count(NodeExpectation.id))
            .where(NodeExpectation.proposal_node_id.in_(node_ids))
            .group_by(NodeExpectation.proposal_node_id)
        )
        expectation_rows = list(self.session.exec(expectation_statement).all())
        has_expectation_map = {row[0]: row[1] > 0 for row in expectation_rows}

        return [(node, has_expectation_map.get(node.id, False)) for node in nodes]

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

    def get_user_by_external_user_id(self, external_user_id: str) -> User | None:
        """Fetch user by external auth identifier."""
        statement = select(User).where(User.email == external_user_id)
        return self.session.exec(statement).first()

    def get_or_create_user_by_external_user_id(self, external_user_id: str) -> User:
        """Fetch existing user by external id or create one."""
        user = self.get_user_by_external_user_id(external_user_id)
        if user is not None:
            return user

        user = User(
            email=external_user_id,
            is_anonymous=False,
        )
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
        *,
        external_user_id: str | None = None,
        idempotency_key: str | None = None,
        request_payload_sha256: str | None = None,
        idempotency_expires_at: datetime | None = None,
    ) -> Review:
        """Create a new review record."""
        review = Review(
            proposal_snippet_id=snippet_id,
            prompt_template_id=template_id,
            external_user_id=external_user_id,
            idempotency_key=idempotency_key,
            request_payload_sha256=request_payload_sha256,
            idempotency_expires_at=idempotency_expires_at,
        )
        self.session.add(review)
        self.session.commit()
        self.session.refresh(review)
        return review

    def get_review_by_id(self, review_id: UUID) -> Review | None:
        """Fetch a review by ID."""
        return self.session.get(Review, review_id)

    def get_review_by_external_user_and_idempotency_key(
        self,
        *,
        external_user_id: str,
        idempotency_key: str,
    ) -> Review | None:
        """Fetch review by idempotency scope."""
        statement = (
            select(Review)
            .where(Review.external_user_id == external_user_id)
            .where(Review.idempotency_key == idempotency_key)
            .order_by(Review.created_at.desc())
        )
        return self.session.exec(statement).first()

    def get_active_review_by_idempotency(
        self,
        *,
        external_user_id: str,
        idempotency_key: str,
        at_time: datetime,
    ) -> Review | None:
        """Fetch unexpired idempotent review, if any."""
        statement = (
            select(Review)
            .where(Review.external_user_id == external_user_id)
            .where(Review.idempotency_key == idempotency_key)
            .where(Review.idempotency_expires_at.is_not(None))
            .where(Review.idempotency_expires_at >= at_time)
            .order_by(Review.created_at.desc())
        )
        return self.session.exec(statement).first()

    def count_reviews_for_external_user_between(
        self,
        *,
        external_user_id: str,
        start_time: datetime,
        end_time: datetime,
    ) -> int:
        """Count reviews created for user within inclusive-exclusive window."""
        statement = (
            select(func.count(Review.id))
            .where(Review.external_user_id == external_user_id)
            .where(Review.created_at >= start_time)
            .where(Review.created_at < end_time)
            .where(Review.idempotency_key.is_not(None))
        )
        return int(self.session.exec(statement).one())

    def get_review_owner_external_user_id(self, review_id: UUID) -> str | None:
        """Fetch owning external user id for a review."""
        statement = (
            select(User.email)
            .join(ProposalSnippet, ProposalSnippet.user_id == User.id)
            .join(Review, Review.proposal_snippet_id == ProposalSnippet.id)
            .where(Review.id == review_id)
        )
        return self.session.exec(statement).first()

    def get_review_cards_ordered(self, review_id: UUID) -> list[ReviewCard]:
        """Fetch review cards ordered by expectation order index."""
        statement = (
            select(ReviewCard)
            .join(NodeExpectation, ReviewCard.node_expectation_id == NodeExpectation.id)
            .where(ReviewCard.review_id == review_id)
            .order_by(NodeExpectation.order_index, ReviewCard.id)
        )
        return list(self.session.exec(statement).all())

    def create_review_card(
        self,
        review_id: UUID,
        expectation_id: UUID,
        rating: ReviewRating,
        feedback: str,
    ) -> ReviewCard:
        """Create a new review card."""
        card = ReviewCard(
            review_id=review_id,
            node_expectation_id=expectation_id,
            rating=rating,
            feedback_text=feedback,
        )
        self.session.add(card)
        self.session.commit()
        self.session.refresh(card)
        return card

    def update_review(
        self,
        review: Review,
    ) -> Review:
        """Update an existing review record."""
        self.session.add(review)
        self.session.commit()
        self.session.refresh(review)
        return review

    def rollback(self) -> None:
        """Rollback active transaction after commit failure."""
        self.session.rollback()
