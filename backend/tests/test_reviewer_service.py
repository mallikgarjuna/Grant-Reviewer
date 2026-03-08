"""backend/tests/test_reviewer_service.py
Representative-call tests for ReviewerService.generate_review.
"""

from __future__ import annotations

from pathlib import Path
from uuid import UUID

import pytest
from sqlmodel import SQLModel, select

from app.db import engine, get_session
from app.models.domain import FundingCall, PromptTemplate, ProposalNode, ReviewCard, ReviewStatus
from app.repositories.review_repository import ReviewRepository
from app.services.llm_client import StubLLMClient
from app.services.reviewer_service import ReviewerService
from scripts.ingest_call import ingest_call


def _reset_database() -> None:
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


def _wf0065_paired_boundary_cases() -> list[dict[str, str]]:
    return [
        {
            "case_id": "nwo_veni_2025_preproposal",
            "call_path": "data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml",
            "call_code": "nwo_veni_2025_preproposal",
            "stage": "STEP_1",
            "node_logical_id": "key_outputs",
            "node_text": "Representative paired-boundary text for NWO key outputs.",
        },
        {
            "case_id": "erc_stg_2026_full",
            "call_path": "data/calls/canonical/erc/erc_stg_2026_full.yaml",
            "call_code": "erc_stg_2026_full",
            "stage": "STEP_2",
            "node_logical_id": "b1_part1_scientific_proposal",
            "node_text": "Representative paired-boundary text for ERC scientific proposal.",
        },
        {
            "case_id": "MSCA-PF-2025",
            "call_path": "data/calls/canonical/msca/msca_pf_2025_full.yaml",
            "call_code": "MSCA-PF-2025",
            "stage": "STEP_1",
            "node_logical_id": "excellence",
            "node_text": "Representative paired-boundary text for MSCA excellence.",
        },
    ]


def _build_service_for_call(
    monkeypatch,
    *,
    call_path: str,
    call_code: str,
    node_logical_id: str,
) -> tuple[ReviewerService, UUID, UUID]:
    monkeypatch.setenv("REVIEW_TIMEOUT_SECONDS", "0.02")
    _reset_database()
    ingest_call(Path(call_path), dry_run=False)

    session = get_session()
    template = PromptTemplate(
        name="WF0065 reviewer service template",
        template_text="Template",
        is_active=True,
    )
    session.add(template)
    session.commit()

    call = session.exec(select(FundingCall).where(FundingCall.code == call_code)).first()
    assert call is not None
    node = session.exec(
        select(ProposalNode).where(
            ProposalNode.funding_call_id == call.id,
            ProposalNode.logical_id == node_logical_id,
        )
    ).first()
    assert node is not None

    repository = ReviewRepository(session)
    service = ReviewerService(
        repository=repository,
        llm_client=StubLLMClient(),
    )
    return service, call.id, node.id


@pytest.mark.parametrize(
    "case",
    _wf0065_paired_boundary_cases(),
    ids=lambda case: f"wf0065_reviewer_service_representative_{case['case_id']}",
)
def test_wf0065_reviewer_service_representative_success_matrix(
    monkeypatch,
    case: dict[str, str],
) -> None:
    service, call_id, node_id = _build_service_for_call(
        monkeypatch,
        call_path=case["call_path"],
        call_code=case["call_code"],
        node_logical_id=case["node_logical_id"],
    )
    try:
        review, cards = service.generate_review(
            node_id=node_id,
            snippet_text=case["node_text"],
            call_id=call_id,
            review_stage=case["stage"],
            external_user_id=f"wf0065-single-service-{case['case_id']}",
            idempotency_key=f"wf0065-single-service-{case['case_id']}",
        )
        assert review.status == ReviewStatus.COMPLETED
        assert review.review_type == "single"
        assert review.proposal_snippet_id is not None
        assert len(cards) >= 1

        persisted_cards = list(
            service.repository.session.exec(
                select(ReviewCard).where(ReviewCard.review_id == review.id)
            ).all()
        )
        assert len(persisted_cards) == len(cards)
    finally:
        service.repository.session.close()
