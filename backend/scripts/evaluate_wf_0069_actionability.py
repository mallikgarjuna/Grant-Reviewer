"""backend/scripts/evaluate_wf_0069_actionability.py
WF-0069 deterministic replay evaluator for actionability/prioritization closure.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from uuid import UUID

from sqlmodel import SQLModel, select

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db import engine, get_session
from app.models.domain import (
    AssessmentStatus,
    FundingCall,
    PromptTemplate,
)
from app.repositories.review_repository import ReviewRepository
from app.services.llm_client import StubLLMClient
from app.services.structured_reviewer_service import StructuredReviewerService
from scripts.ingest_call import ingest_call

LOCKED_CALL_TO_PATH: dict[str, str] = {
    "nwo_veni_2025_preproposal": "data/calls/canonical/nwo/nwo_veni_2025_preproposal.yaml",
    "erc_stg_2026_full": "data/calls/canonical/erc/erc_stg_2026_full.yaml",
    "MSCA-PF-2025": "data/calls/canonical/msca/msca_pf_2025_full.yaml",
}
STRESS_ITEM_IDS: set[str] = {
    "wf0068_nwo_actionability_prioritization_stress",
    "wf0068_erc_actionability_prioritization_stress",
    "wf0068_msca_actionability_prioritization_stress",
}
BASELINE_ITEM_IDS: set[str] = {
    "wf0068_nwo_baseline_representative",
    "wf0068_erc_baseline_representative",
    "wf0068_msca_baseline_representative",
}
REQUIRED_ITEM_IDS: set[str] = STRESS_ITEM_IDS | BASELINE_ITEM_IDS
REQUIRED_ITEM_CALL_BY_ID: dict[str, str] = {
    "wf0068_nwo_actionability_prioritization_stress": "nwo_veni_2025_preproposal",
    "wf0068_erc_actionability_prioritization_stress": "erc_stg_2026_full",
    "wf0068_msca_actionability_prioritization_stress": "MSCA-PF-2025",
    "wf0068_nwo_baseline_representative": "nwo_veni_2025_preproposal",
    "wf0068_erc_baseline_representative": "erc_stg_2026_full",
    "wf0068_msca_baseline_representative": "MSCA-PF-2025",
}
REQUIRED_ITEM_ROLE_BY_ID: dict[str, str] = {
    "wf0068_nwo_actionability_prioritization_stress": "actionability_prioritization_stress",
    "wf0068_erc_actionability_prioritization_stress": "actionability_prioritization_stress",
    "wf0068_msca_actionability_prioritization_stress": "actionability_prioritization_stress",
    "wf0068_nwo_baseline_representative": "baseline_representative",
    "wf0068_erc_baseline_representative": "baseline_representative",
    "wf0068_msca_baseline_representative": "baseline_representative",
}
DIMENSION_STATES: tuple[str, ...] = ("fail", "weak", "pass")
STATE_RANK: dict[str, int] = {"fail": 0, "weak": 1, "pass": 2}
BASELINE_FLOOR_BY_ITEM: dict[str, dict[str, str]] = {
    item_id: {
        "revision_actionability": "weak",
        "prioritization_quality": "weak",
    }
    for item_id in BASELINE_ITEM_IDS
}


@dataclass(frozen=True)
class CardSignal:
    assessed_indices: list[int]
    actionable_assessed_indices: list[int]
    not_assessable_indices: list[int]
    flat_status_assessed_indices: list[int]
    fail_closed_missing_reason_indices: list[int]


def _load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"INVALID_JSON_OBJECT: {path}")
    return payload


def _is_test_database_url(database_url: str) -> bool:
    database_name = urlparse(database_url).path.strip("/").lower()
    return "test" in database_name


def _validate_safe_database_url_for_reset() -> None:
    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url:
        raise ValueError("DATABASE_URL_REQUIRED_FOR_RESET")
    if not _is_test_database_url(database_url):
        raise ValueError(f"UNSAFE_DATABASE_URL_FOR_RESET: {database_url}")


def _reset_db() -> None:
    _validate_safe_database_url_for_reset()
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


def _bootstrap_locked_calls() -> None:
    for call_path in LOCKED_CALL_TO_PATH.values():
        ingest_call(Path(call_path), dry_run=False)


def _ensure_prompt_template(session) -> None:
    template = PromptTemplate(
        name="WF0069 actionability evaluator template",
        template_text="Template",
        is_active=True,
    )
    session.add(template)
    session.commit()


def _get_call_id_by_code(repository: ReviewRepository, *, call_code: str) -> UUID:
    statement = select(FundingCall).where(FundingCall.code == call_code)
    call = repository.session.exec(statement).first()
    if call is None:
        raise ValueError(f"CALL_NOT_FOUND: {call_code}")
    return call.id


def _card_signals(cards: list[dict[str, Any]]) -> CardSignal:
    assessed_indices: list[int] = []
    actionable_assessed_indices: list[int] = []
    not_assessable_indices: list[int] = []
    flat_status_assessed_indices: list[int] = []
    fail_closed_missing_reason_indices: list[int] = []

    for index, card in enumerate(cards):
        status = card.get("assessment_status")
        feedback_text = str(card.get("feedback_text", ""))
        not_assessable_reason = card.get("not_assessable_reason")

        if status == AssessmentStatus.ASSESSED:
            assessed_indices.append(index)
            if feedback_text.startswith("Revise "):
                actionable_assessed_indices.append(index)
            if feedback_text.strip() == "content_evaluated":
                flat_status_assessed_indices.append(index)
        elif status == AssessmentStatus.NOT_ASSESSABLE:
            not_assessable_indices.append(index)
            if not isinstance(not_assessable_reason, str) or not not_assessable_reason.strip():
                fail_closed_missing_reason_indices.append(index)

    return CardSignal(
        assessed_indices=assessed_indices,
        actionable_assessed_indices=actionable_assessed_indices,
        not_assessable_indices=not_assessable_indices,
        flat_status_assessed_indices=flat_status_assessed_indices,
        fail_closed_missing_reason_indices=fail_closed_missing_reason_indices,
    )


def _classify_dimensions(cards: list[dict[str, Any]]) -> tuple[dict[str, str], CardSignal]:
    signals = _card_signals(cards)

    if signals.actionable_assessed_indices and not signals.flat_status_assessed_indices:
        revision_actionability = "pass"
    elif signals.actionable_assessed_indices or signals.assessed_indices:
        revision_actionability = "weak"
    else:
        revision_actionability = "fail"

    if not signals.actionable_assessed_indices:
        prioritization_quality = "fail"
    elif not signals.not_assessable_indices:
        prioritization_quality = "pass"
    else:
        first_actionable = min(signals.actionable_assessed_indices)
        first_context_gap = min(signals.not_assessable_indices)
        prioritization_quality = "pass" if first_actionable < first_context_gap else "weak"

    return (
        {
            "revision_actionability": revision_actionability,
            "prioritization_quality": prioritization_quality,
        },
        signals,
    )


def _meets_floor(observed: str, required_floor: str) -> bool:
    return STATE_RANK[observed] >= STATE_RANK[required_floor]


def _evaluate_item(cards: list[dict[str, Any]], *, role: str, item_id: str) -> dict[str, Any]:
    dimensions, signals = _classify_dimensions(cards)
    floor = BASELINE_FLOOR_BY_ITEM.get(item_id)
    floor_checks: dict[str, bool] = {}
    if floor is not None:
        for dimension, required_floor in floor.items():
            floor_checks[dimension] = _meets_floor(dimensions[dimension], required_floor)

    stress_pass = True
    if role == "actionability_prioritization_stress":
        stress_pass = (
            dimensions["revision_actionability"] == "pass"
            and dimensions["prioritization_quality"] == "pass"
        )

    return {
        "dimension_scores": dimensions,
        "signals": {
            "assessed_indices": signals.assessed_indices,
            "actionable_assessed_indices": signals.actionable_assessed_indices,
            "not_assessable_indices": signals.not_assessable_indices,
            "flat_status_assessed_indices": signals.flat_status_assessed_indices,
            "fail_closed_missing_reason_indices": signals.fail_closed_missing_reason_indices,
        },
        "stress_gate_pass": stress_pass,
        "baseline_floor_checks": floor_checks,
    }


def _extract_required_items(batch: dict[str, Any]) -> list[dict[str, Any]]:
    raw_items = batch.get("items")
    if not isinstance(raw_items, list):
        raise ValueError("INVALID_BATCH_ITEMS")

    selected: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw_item in raw_items:
        if not isinstance(raw_item, dict):
            continue
        item_id = str(raw_item.get("item_id", ""))
        if item_id not in REQUIRED_ITEM_IDS:
            continue
        if item_id in seen:
            raise ValueError(f"DUPLICATE_ITEM_ID: {item_id}")
        seen.add(item_id)
        expected_call_id = REQUIRED_ITEM_CALL_BY_ID[item_id]
        actual_call_id = str(raw_item.get("call_id", ""))
        if actual_call_id != expected_call_id:
            raise ValueError(
                f"ITEM_CALL_ID_MISMATCH: {item_id} expected {expected_call_id} got {actual_call_id}"
            )
        expected_role = REQUIRED_ITEM_ROLE_BY_ID[item_id]
        actual_role = str(raw_item.get("role", ""))
        if actual_role != expected_role:
            raise ValueError(
                f"ITEM_ROLE_MISMATCH: {item_id} expected {expected_role} got {actual_role}"
            )
        selected.append(raw_item)

    if seen != REQUIRED_ITEM_IDS:
        missing = sorted(REQUIRED_ITEM_IDS - seen)
        raise ValueError(f"MISSING_REQUIRED_ITEMS: {','.join(missing)}")

    return sorted(selected, key=lambda item: int(item.get("batch_order", 0)))


def evaluate_wf_0069_actionability(
    *,
    batch: dict[str, Any],
    baseline: dict[str, Any],
) -> dict[str, Any]:
    baseline_id = str(baseline.get("baseline_id", "")).strip()
    if not baseline_id:
        raise ValueError("INVALID_BASELINE_ID")

    selected_items = _extract_required_items(batch)

    _reset_db()
    _bootstrap_locked_calls()

    session = get_session()
    repository = ReviewRepository(session)
    _ensure_prompt_template(session)
    service = StructuredReviewerService(repository=repository, llm_client=StubLLMClient())

    evaluated_items: list[dict[str, Any]] = []
    stress_failures: list[str] = []
    baseline_floor_failures: list[str] = []

    try:
        for item in selected_items:
            call_code = str(item["call_id"])
            call_id = _get_call_id_by_code(repository, call_code=call_code)
            review, cards = service.generate_structured_review_pipeline_v1(
                review_stage=str(item.get("review_stage", "STEP_1")),
                call_id=call_id,
                nodes=[(str(item["node_logical_id"]), str(item["snippet_text"]))],
                external_user_id="wf0069-evaluator",
                idempotency_key=f"wf0069-evaluator:{item['item_id']}",
            )
            card_payloads = [
                {
                    "node_logical_id": card.expectation.node.logical_id if card.expectation and card.expectation.node else None,
                    "assessment_status": card.assessment_status,
                    "feedback_text": card.feedback_text,
                    "not_assessable_reason": card.not_assessable_reason,
                }
                for card in cards
            ]
            item_eval = _evaluate_item(
                card_payloads,
                role=str(item.get("role", "")),
                item_id=str(item["item_id"]),
            )
            if str(item.get("role", "")) == "actionability_prioritization_stress" and not item_eval["stress_gate_pass"]:
                stress_failures.append(str(item["item_id"]))
            if item_eval["baseline_floor_checks"] and not all(item_eval["baseline_floor_checks"].values()):
                baseline_floor_failures.append(str(item["item_id"]))

            evaluated_items.append(
                {
                    "item_id": str(item["item_id"]),
                    "call_id": call_code,
                    "role": str(item.get("role", "")),
                    "review_status": review.status.value,
                    "card_count": len(cards),
                    **item_eval,
                }
            )

        nwo_call = session.exec(
            select(FundingCall).where(FundingCall.code == "nwo_veni_2025_preproposal")
        ).first()
        if nwo_call is None:
            raise ValueError("CALL_NOT_FOUND: nwo_veni_2025_preproposal")

        guard_review, guard_cards = service.generate_structured_review_pipeline_v1(
            review_stage="STEP_1",
            call_id=nwo_call.id,
            nodes=[("research_idea", "Fail-closed guard text for alignment context.")],
            external_user_id="wf0069-evaluator-guard",
            idempotency_key="wf0069-evaluator:fail-closed-guard",
        )
        guard_payloads = [
            {
                "assessment_status": card.assessment_status,
                "not_assessable_reason": card.not_assessable_reason,
            }
            for card in guard_cards
        ]
        guard_not_assessable = [
            card for card in guard_payloads if card["assessment_status"] == AssessmentStatus.NOT_ASSESSABLE
        ]
        fail_closed_guard_pass = bool(guard_not_assessable) and all(
            isinstance(card.get("not_assessable_reason"), str)
            and bool(card["not_assessable_reason"].strip())
            for card in guard_not_assessable
        )
    finally:
        session.close()

    stress_gate_pass = not stress_failures
    baseline_floor_gate_pass = not baseline_floor_failures
    overall_pass = stress_gate_pass and baseline_floor_gate_pass and fail_closed_guard_pass

    return {
        "artifact_type": "wf0069_actionability_evaluation_v1",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "batch_id": str(batch.get("batch_id", "")),
        "baseline_id": baseline_id,
        "evaluated_item_ids": [item["item_id"] for item in evaluated_items],
        "evaluated_items": evaluated_items,
        "stress_gate": {
            "pass": stress_gate_pass,
            "failing_item_ids": sorted(stress_failures),
        },
        "baseline_floor_gate": {
            "pass": baseline_floor_gate_pass,
            "failing_item_ids": sorted(baseline_floor_failures),
            "required_floor": "weak",
        },
        "fail_closed_guard": {
            "pass": fail_closed_guard_pass,
            "review_status": guard_review.status.value,
            "not_assessable_card_count": len(guard_not_assessable),
        },
        "overall_pass": overall_pass,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="WF-0069 deterministic replay evaluator for actionability remediation.",
    )
    parser.add_argument("--batch", type=Path, required=True, help="WF-0068 snippet batch manifest path")
    parser.add_argument("--baseline", type=Path, required=True, help="WF-0068 baseline JSON path")
    parser.add_argument("--output", type=Path, required=True, help="Output JSON path")
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    batch = _load_json_object(args.batch)
    baseline = _load_json_object(args.baseline)
    payload = evaluate_wf_0069_actionability(batch=batch, baseline=baseline)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote WF-0069 actionability evaluation: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
