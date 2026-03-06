"""backend/app/repositories/review_repository.py
Review repository - database access layer.

Rule: Only repositories talk to the database directly.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import func, or_
from sqlmodel import Session, select

from app.models.domain import (
    AssessmentStatus,
    CallDefinition,
    EvaluationCriterion,
    EvaluationElement,
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
        statement = select(ProposalNode).where(
            ProposalNode.id == node_id,
            ProposalNode.archived_at.is_(None),
        )
        return self.session.exec(statement).first()

    def get_call_by_id(self, call_id: UUID) -> FundingCall | None:
        """Fetch a funding call by ID."""
        return self.session.get(FundingCall, call_id)

    def get_active_call_by_code(self, call_code: str) -> FundingCall | None:
        """Fetch an active funding call by stable code/logical id."""
        statement = select(FundingCall).where(
            FundingCall.code == call_code,
            FundingCall.is_active,
        )
        return self.session.exec(statement).first()

    def get_call_definition_by_call_id(self, call_id: UUID) -> CallDefinition | None:
        """Fetch canonical call-definition document for a funding call."""
        statement = select(CallDefinition).where(CallDefinition.funding_call_id == call_id)
        return self.session.exec(statement).first()

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
            .where(
                ProposalNode.funding_call_id == call_id,
                ProposalNode.archived_at.is_(None),
            )
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
        template_id: UUID,
        snippet_id: UUID | None = None,
        *,
        external_user_id: str | None = None,
        idempotency_key: str | None = None,
        request_payload_sha256: str | None = None,
        idempotency_expires_at: datetime | None = None,
        review_type: str = "single",
        structured_payload: dict[str, Any] | None = None,
    ) -> Review:
        """Create a new review record."""
        review = Review(
            proposal_snippet_id=snippet_id,
            prompt_template_id=template_id,
            external_user_id=external_user_id,
            idempotency_key=idempotency_key,
            request_payload_sha256=request_payload_sha256,
            idempotency_expires_at=idempotency_expires_at,
            review_type=review_type,
            structured_payload=structured_payload,
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
        review = self.get_review_by_id(review_id)
        if review is None:
            return None
        if review.proposal_snippet_id is None:
            return review.external_user_id

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
            .join(ProposalNode, NodeExpectation.proposal_node_id == ProposalNode.id)
            .where(ReviewCard.review_id == review_id)
            .order_by(ProposalNode.order_index, NodeExpectation.order_index, ReviewCard.id)
        )
        return list(self.session.exec(statement).all())

    def get_review_cards_with_criteria(
        self, review_id: UUID
    ) -> list[
        tuple[ReviewCard, str, str | None, str, str | None, str | None, str]
    ]:
        """Fetch review cards with criterion and expectation metadata ordered by expectation index.

        Historical review rendering should remain stable even if evaluation elements/criteria
        are archived after the review was created, so this query intentionally does not filter
        on archived flags for those tables.
        """
        statement = (
            select(
                ReviewCard,
                EvaluationCriterion.name,
                EvaluationCriterion.description,
                EvaluationElement.name,
                NodeExpectation.guidance_note,
                ProposalNode.logical_id,
                ProposalNode.title,
            )
            .join(NodeExpectation, ReviewCard.node_expectation_id == NodeExpectation.id)
            .join(ProposalNode, NodeExpectation.proposal_node_id == ProposalNode.id)
            .join(
                EvaluationElement,
                NodeExpectation.evaluation_element_id == EvaluationElement.id,
            )
            .join(
                EvaluationCriterion,
                EvaluationElement.evaluation_criterion_id == EvaluationCriterion.id,
            )
            .where(ReviewCard.review_id == review_id)
            .order_by(ProposalNode.order_index, NodeExpectation.order_index, ReviewCard.id)
        )
        return list(self.session.exec(statement).all())

    def delete_review_hard(self, review_id: UUID) -> bool:
        """Hard-delete review, cards, and associated snippet."""
        review = self.get_review_by_id(review_id)
        if review is None:
            return False

        snippet = None
        if review.proposal_snippet_id is not None:
            snippet = self.session.get(ProposalSnippet, review.proposal_snippet_id)
        cards = self.get_review_cards_ordered(review_id)

        for card in cards:
            self.session.delete(card)
        self.session.delete(review)
        if snippet is not None:
            self.session.delete(snippet)

        self.session.commit()
        return True

    def create_review_card(
        self,
        review_id: UUID,
        expectation_id: UUID,
        rating: ReviewRating,
        feedback: str,
        assessment_status: AssessmentStatus = AssessmentStatus.ASSESSED,
        not_assessable_reason: str | None = None,
    ) -> ReviewCard:
        """Create a new review card."""
        card = ReviewCard(
            review_id=review_id,
            node_expectation_id=expectation_id,
            rating=rating,
            feedback_text=feedback,
            assessment_status=assessment_status,
            not_assessable_reason=not_assessable_reason,
        )
        self.session.add(card)
        self.session.commit()
        self.session.refresh(card)
        return card

    def create_review_cards_batch(
        self,
        *,
        review_id: UUID,
        cards: list[tuple[UUID, ReviewRating, str, AssessmentStatus, str | None]],
    ) -> list[ReviewCard]:
        """Create many review cards atomically with a single commit."""
        created_cards: list[ReviewCard] = []
        for expectation_id, rating, feedback, assessment_status, not_assessable_reason in cards:
            created_cards.append(
                ReviewCard(
                    review_id=review_id,
                    node_expectation_id=expectation_id,
                    rating=rating,
                    feedback_text=feedback,
                    assessment_status=assessment_status,
                    not_assessable_reason=not_assessable_reason,
                )
            )

        self.session.add_all(created_cards)
        self.session.commit()
        for card in created_cards:
            self.session.refresh(card)
        return created_cards

    def update_review(
        self,
        review: Review,
    ) -> Review:
        """Update an existing review record."""
        self.session.add(review)
        self.session.commit()
        self.session.refresh(review)
        return review

    def resolve_structured_review_coverage(
        self,
        review: Review,
    ) -> tuple[list[str], list[str], list[str]]:
        """Resolve persisted submitted-leaf coverage and legacy compatibility metadata."""
        payload = review.structured_payload
        if not isinstance(payload, dict):
            return [], [], []

        def _parse_string_list(value: Any) -> list[str]:
            if not isinstance(value, list):
                return []
            parsed: list[str] = []
            for item in value:
                if isinstance(item, str) and item.strip():
                    parsed.append(item.strip())
            return parsed

        submitted_leaf_ids = _parse_string_list(payload.get("submitted_leaf_ids"))
        legacy_ambiguous_container_ids = _parse_string_list(
            payload.get("legacy_ambiguous_container_ids")
        )
        moved_legacy_node_references = _parse_string_list(
            payload.get("moved_legacy_node_references")
        )

        nodes = payload.get("nodes")
        submitted_node_ids = (
            [key for key in nodes.keys() if isinstance(key, str) and key.strip()]
            if isinstance(nodes, dict)
            else []
        )
        erc_container_ids = {"part_a", "budget", "part_b", "b1", "b2"}

        if not submitted_leaf_ids:
            submitted_leaf_ids = sorted(
                [
                    node_id
                    for node_id in submitted_node_ids
                    if node_id not in erc_container_ids
                ]
            )
        if not legacy_ambiguous_container_ids:
            legacy_ambiguous_container_ids = sorted(
                [node_id for node_id in submitted_node_ids if node_id in {"b1", "b2"}]
            )

        call_code: str | None = None
        payload_call_id = payload.get("call_id")
        if isinstance(payload_call_id, str):
            try:
                resolved_call = self.session.get(FundingCall, UUID(payload_call_id))
                call_code = resolved_call.code if resolved_call is not None else None
            except ValueError:
                call_code = None
        if (
            not moved_legacy_node_references
            and "resources_time_commitment" in submitted_node_ids
            and "submitted_leaf_ids" not in payload
            and call_code == "erc_stg_2026_full"
        ):
            moved_legacy_node_references = ["resources_time_commitment"]

        return (
            submitted_leaf_ids,
            legacy_ambiguous_container_ids,
            moved_legacy_node_references,
        )

    def rollback(self) -> None:
        """Rollback active transaction after commit failure."""
        self.session.rollback()

    def list_reviews_for_external_user(
        self,
        external_user_id: str,
        *,
        limit: int = 50,
    ) -> list[tuple[Review, str, str]]:
        """List reviews owned by an external user with call name and node title.

        Returns list of (Review, call_name, node_title) tuples ordered
        by created_at descending.
        """
        capped_limit = min(max(limit, 1), 100)
        statement = (
            select(
                Review,
                FundingCall.name,
                func.coalesce(ProposalNode.title, "Structured review"),
                Review.structured_payload,
            )
            .join(
                ProposalSnippet,
                Review.proposal_snippet_id == ProposalSnippet.id,
                isouter=True,
            )
            .join(
                FundingCall,
                ProposalSnippet.funding_call_id == FundingCall.id,
                isouter=True,
            )
            .join(
                ProposalNode,
                ProposalSnippet.proposal_node_id == ProposalNode.id,
                isouter=True,
            )
            .where(Review.external_user_id == external_user_id)
            .where(
                or_(
                    ProposalNode.archived_at.is_(None),
                    ProposalNode.id.is_(None),
                )
            )
            .order_by(Review.created_at.desc())
            .limit(capped_limit)
        )
        rows = list(self.session.exec(statement).all())

        normalized_rows: list[tuple[Review, str, str]] = []
        for review, call_name, node_title, structured_payload in rows:
            resolved_call_name = call_name
            if resolved_call_name is None and isinstance(structured_payload, dict):
                payload_call_name = structured_payload.get("call_name")
                if isinstance(payload_call_name, str) and payload_call_name.strip():
                    resolved_call_name = payload_call_name.strip()

            normalized_rows.append(
                (
                    review,
                    resolved_call_name or "Structured review",
                    node_title,
                )
            )

        return normalized_rows
