"""backend/scripts/validate_wf_0068_evidence_bundle.py
WF-0068 evidence-bundle validator with explicit records/bundle modes.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

DIMENSION_KEYS: set[str] = {
    "criteria_groundedness",
    "official_traceability",
    "revision_actionability",
    "specificity_without_false_specificity",
    "prioritization_quality",
}
DIMENSION_STATES: set[str] = {"pass", "weak", "fail", "insufficient_evidence"}
SEVERITY_LEVELS: set[str] = {"high", "medium", "low"}
FAILURE_TAGS: set[str] = {
    "genericity",
    "false_specificity",
    "weak_traceability",
    "bad_prioritization",
    "low_actionability",
    "criteria_element_mismatch",
}
FOLLOW_ON_PATTERN_CLASSES: set[str] = {
    "none",
    "evidence_gap",
    "genericity_cluster",
    "false_specificity_cluster",
    "traceability_cluster",
    "prioritization_cluster",
    "actionability_cluster",
    "criteria_element_alignment_cluster",
    "mixed_cluster",
}
FOLLOW_ON_DECISIONS: set[str] = {
    "no_follow_on_wf",
    "proceed_to_narrow_follow_on_wf",
    "more_evidence_required",
}
MISSION_RESULTS: set[str] = {"pass", "fail", "inconclusive"}


def _load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"INVALID_JSON_OBJECT: {path}")
    return payload


def _read_case(path: Path, case_name: str) -> dict[str, Any]:
    payload = _load_json_object(path)
    cases = payload.get("cases")
    if not isinstance(cases, dict) or case_name not in cases:
        raise ValueError(f"CASE_NOT_FOUND: {case_name}")
    case_payload = cases[case_name]
    if not isinstance(case_payload, dict):
        raise ValueError(f"INVALID_CASE_PAYLOAD: {case_name}")
    return case_payload


def _ensure_non_empty_str(value: Any, *, code: str, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{code}: {context}")
    return value


def _validate_baseline_required_fields(baseline: dict[str, Any]) -> None:
    required_keys = {
        "baseline_id",
        "app_commit_sha",
        "app_branch_ref",
        "prompt_config_ref",
        "model_runtime_ref",
        "reviewer_instruction_ref",
        "evidence_template_version",
        "dimension_scale",
    }
    missing = sorted(required_keys - set(baseline))
    if missing:
        raise ValueError(f"BASELINE_FIELDS_MISSING: {','.join(missing)}")
    if baseline.get("dimension_scale") != ["pass", "weak", "fail", "insufficient_evidence"]:
        raise ValueError("DIMENSION_SCALE_INVALID: baseline.dimension_scale")


def _validate_official_locator(locator: Any) -> None:
    locator_value = _ensure_non_empty_str(
        locator,
        code="OFFICIAL_LOCATOR_MISSING",
        context="official_locator_used",
    )
    # Require a replayable locator shape (path-like + anchor-like component).
    if "/" not in locator_value or not re.search(r"[#:]", locator_value):
        raise ValueError("OFFICIAL_LOCATOR_NON_REPLAYABLE")


def _validate_dimension_scores(dimension_scores: Any) -> None:
    if not isinstance(dimension_scores, dict):
        raise ValueError("DIMENSION_SCALE_INVALID: dimension_scores must be object")
    keys = set(dimension_scores)
    if keys != DIMENSION_KEYS:
        raise ValueError("DIMENSION_SCALE_INVALID: dimension_scores keys mismatch")
    for key, value in dimension_scores.items():
        if value not in DIMENSION_STATES:
            raise ValueError(f"DIMENSION_STATE_INVALID: {key}")


def _validate_item_enums(item: dict[str, Any]) -> None:
    severity = item.get("severity")
    if severity not in SEVERITY_LEVELS:
        raise ValueError("SEVERITY_INVALID")

    failure_tags = item.get("failure_tags")
    if not isinstance(failure_tags, list):
        raise ValueError("FAILURE_TAG_INVALID")
    for tag in failure_tags:
        if tag not in FAILURE_TAGS:
            raise ValueError("FAILURE_TAG_INVALID")

    pattern_class = item.get("follow_on_pattern_class")
    if pattern_class not in FOLLOW_ON_PATTERN_CLASSES:
        raise ValueError("FOLLOW_ON_PATTERN_CLASS_INVALID")


def _validate_records_consistency(records: dict[str, Any], raw_output: dict[str, Any], baseline: dict[str, Any]) -> None:
    _validate_baseline_required_fields(baseline)

    records_items = records.get("items")
    raw_items = raw_output.get("items")
    if not isinstance(records_items, list) or not isinstance(raw_items, list):
        raise ValueError("RECORDS_OR_RAW_ITEMS_INVALID")
    if len(records_items) != len(raw_items):
        raise ValueError("ITEM_COUNT_MISMATCH")

    baseline_id = _ensure_non_empty_str(
        baseline.get("baseline_id"),
        code="BASELINE_INVALID",
        context="baseline_id",
    )
    if records.get("baseline_id") != baseline_id:
        raise ValueError("BASELINE_REFERENCE_MISMATCH: records baseline_id")

    raw_item_ids = {str(item.get("item_id")) for item in raw_items if isinstance(item, dict)}
    raw_baseline_ids = {str(item.get("baseline_id")) for item in raw_items if isinstance(item, dict)}
    if raw_baseline_ids != {baseline_id}:
        raise ValueError("BASELINE_REFERENCE_MISMATCH: raw output baseline_id")

    for item in records_items:
        if not isinstance(item, dict):
            raise ValueError("INVALID_RECORD_ITEM")
        item_id = _ensure_non_empty_str(item.get("item_id"), code="ITEM_ID_MISSING", context="item_id")
        if item_id not in raw_item_ids:
            raise ValueError("ITEM_REF_MISMATCH")

        _ensure_non_empty_str(item.get("call_id"), code="CALL_ID_MISSING", context=item_id)
        _ensure_non_empty_str(item.get("snippet_id"), code="SNIPPET_ID_MISSING", context=item_id)
        _ensure_non_empty_str(
            item.get("review_output_ref"),
            code="REVIEW_OUTPUT_REF_MISSING",
            context=item_id,
        )
        _ensure_non_empty_str(
            item.get("criterion_or_element_target"),
            code="TARGET_MISSING",
            context=item_id,
        )
        _validate_official_locator(item.get("official_locator_used"))
        _validate_dimension_scores(item.get("dimension_scores"))
        _validate_item_enums(item)

        insufficient_reason = item.get("insufficient_evidence_reason", "")
        has_insufficient_state = any(
            value == "insufficient_evidence"
            for value in item["dimension_scores"].values()
        )
        if isinstance(insufficient_reason, str) and insufficient_reason.strip() and not has_insufficient_state:
            raise ValueError("INSUFFICIENT_EVIDENCE_STATE_REQUIRED")


def validate_records_payload(
    *,
    records: dict[str, Any],
    raw_output: dict[str, Any],
    baseline: dict[str, Any],
) -> None:
    _validate_records_consistency(records, raw_output, baseline)


def _repeated_pattern_calls(records: dict[str, Any]) -> dict[str, set[str]]:
    repeated: dict[str, set[str]] = {}
    counts: dict[str, int] = {}

    items = records.get("items")
    if not isinstance(items, list):
        raise ValueError("RECORDS_OR_RAW_ITEMS_INVALID")

    for item in items:
        if not isinstance(item, dict):
            continue
        pattern = str(item.get("follow_on_pattern_class", ""))
        if pattern in {"", "none", "evidence_gap"}:
            continue
        counts[pattern] = counts.get(pattern, 0) + 1
        repeated.setdefault(pattern, set()).add(str(item.get("call_id", "")))

    return {pattern: calls for pattern, calls in repeated.items() if counts.get(pattern, 0) >= 2}


def validate_bundle_payload(
    *,
    summary: dict[str, Any],
    records: dict[str, Any],
    raw_output: dict[str, Any],
    baseline: dict[str, Any],
) -> None:
    validate_records_payload(records=records, raw_output=raw_output, baseline=baseline)

    required_summary_keys = {
        "batch_id",
        "verification_evidence_bundle_ref",
        "coverage_status",
        "baseline_consistency_status",
        "pattern_summary",
        "mission_result",
        "follow_on_decision",
        "decision_rationale",
        "recommended_follow_on_boundary",
    }
    missing_summary = sorted(required_summary_keys - set(summary))
    if missing_summary:
        raise ValueError(f"SUMMARY_FIELDS_MISSING: {','.join(missing_summary)}")

    if summary.get("mission_result") not in MISSION_RESULTS:
        raise ValueError("MISSION_RESULT_INVALID")
    decision = summary.get("follow_on_decision")
    if decision not in FOLLOW_ON_DECISIONS:
        raise ValueError("FOLLOW_ON_DECISION_INVALID")

    repeated_patterns = _repeated_pattern_calls(records)

    if decision == "proceed_to_narrow_follow_on_wf":
        verification_ref = _ensure_non_empty_str(
            summary.get("verification_evidence_bundle_ref"),
            code="VERIFICATION_BUNDLE_REF_MISSING",
            context="verification_evidence_bundle_ref",
        )
        if not verification_ref:
            raise ValueError("VERIFICATION_BUNDLE_REF_MISSING")

        if not repeated_patterns:
            raise ValueError("REPEATED_PATTERN_REQUIRED")

        boundary = _ensure_non_empty_str(
            summary.get("recommended_follow_on_boundary"),
            code="FOLLOW_ON_BOUNDARY_MISSING",
            context="recommended_follow_on_boundary",
        )
        calls_for_boundary = repeated_patterns.get(boundary)
        if calls_for_boundary is None:
            # Boundary can still be broader textual label only if one repeated class exists.
            if len(repeated_patterns) == 1:
                calls_for_boundary = next(iter(repeated_patterns.values()))
            else:
                raise ValueError("FOLLOW_ON_BOUNDARY_UNSUPPORTED")

        if len(calls_for_boundary) == 1 and "call-specific" not in boundary.lower():
            raise ValueError("CROSS_WEDGE_OVERCLAIM")


def _resolve_payloads_for_records_mode(
    *,
    input_path: Path,
    case_name: str | None,
    raw_output_path: Path | None,
    baseline_path: Path | None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    if case_name:
        case = _read_case(input_path, case_name)
        return (
            _load_json_object_from_value(case.get("records"), "records"),
            _load_json_object_from_value(case.get("raw_output"), "raw_output"),
            _load_json_object_from_value(case.get("baseline"), "baseline"),
        )

    if raw_output_path is None or baseline_path is None:
        raise ValueError("MODE_RECORDS_REQUIRES_RAW_OUTPUT_AND_BASELINE")

    return (
        _load_json_object(input_path),
        _load_json_object(raw_output_path),
        _load_json_object(baseline_path),
    )


def _resolve_payloads_for_bundle_mode(
    *,
    input_path: Path,
    case_name: str | None,
    records_path: Path | None,
    raw_output_path: Path | None,
    baseline_path: Path | None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    if case_name:
        case = _read_case(input_path, case_name)
        return (
            _load_json_object_from_value(case.get("summary"), "summary"),
            _load_json_object_from_value(case.get("records"), "records"),
            _load_json_object_from_value(case.get("raw_output"), "raw_output"),
            _load_json_object_from_value(case.get("baseline"), "baseline"),
        )

    if records_path is None or raw_output_path is None or baseline_path is None:
        raise ValueError("MODE_BUNDLE_REQUIRES_RECORDS_RAW_OUTPUT_BASELINE")

    return (
        _load_json_object(input_path),
        _load_json_object(records_path),
        _load_json_object(raw_output_path),
        _load_json_object(baseline_path),
    )


def _load_json_object_from_value(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"INVALID_CASE_PAYLOAD: {label}")
    return value


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate WF-0068 evidence records/bundle with fail-closed checks.",
    )
    parser.add_argument("--mode", required=True, choices=["records", "bundle"])
    parser.add_argument("input", type=Path, help="Records JSON, summary JSON, or case fixture")
    parser.add_argument("--case", type=str, help="Case name in fixture payload")
    parser.add_argument("--raw-output", type=Path, help="Raw review output JSON path")
    parser.add_argument("--baseline", type=Path, help="Baseline JSON path")
    parser.add_argument("--records", type=Path, help="Evidence records JSON path")
    return parser


def main() -> int:
    args = _build_parser().parse_args()

    if args.mode == "records":
        records, raw_output, baseline = _resolve_payloads_for_records_mode(
            input_path=args.input,
            case_name=args.case,
            raw_output_path=args.raw_output,
            baseline_path=args.baseline,
        )
        validate_records_payload(records=records, raw_output=raw_output, baseline=baseline)
    else:
        summary, records, raw_output, baseline = _resolve_payloads_for_bundle_mode(
            input_path=args.input,
            case_name=args.case,
            records_path=args.records,
            raw_output_path=args.raw_output,
            baseline_path=args.baseline,
        )
        validate_bundle_payload(
            summary=summary,
            records=records,
            raw_output=raw_output,
            baseline=baseline,
        )

    print(f"WF-0068 evidence validation passed (mode={args.mode})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
