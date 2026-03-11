"""backend/scripts/validate_wf_0072_bundle.py
WF-0072 verification-matrix validator.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

LOCKED_REPRESENTATIVE_CALLS: tuple[str, ...] = (
    "nwo_veni_2025_preproposal",
    "erc_stg_2026_full",
    "MSCA-PF-2025",
)
ALLOWED_PROOF_SURFACES: set[str] = {"browser", "API", "paired"}
ALLOWED_AUTH_LANES: set[str] = {"test_bypass", "clerk", "n/a"}
ALLOWED_LANE_STATUS: set[str] = {"executed", "skipped"}
ALLOWED_SCENARIO_TYPES: set[str] = {"positive", "negative"}
ALLOWED_RESULTS: set[str] = {"pass", "fail", "skip"}
REQUIRED_ROW_FIELDS: tuple[str, ...] = (
    "row_id",
    "proof_item_id",
    "call_id",
    "scenario_id",
    "scenario_type",
    "proof_surface",
    "entrypoint",
    "protected_surface",
    "auth_lane",
    "lane_status",
    "scenario_scope_note",
    "deterministic_replay",
    "side_effect_assertion",
    "evidence_ref",
    "result",
)


def _load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("MATRIX_OBJECT_REQUIRED")
    return payload


def _require_non_empty_string(value: Any, *, code: str, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{code}: {context}")
    return value.strip()


def _validate_replay_metadata(row: dict[str, Any]) -> None:
    replay = row.get("deterministic_replay")
    if not isinstance(replay, dict):
        raise ValueError("REPLAY_METADATA_INCOMPLETE")
    for field_name in ("command", "test_id", "assertion_id"):
        _require_non_empty_string(
            replay.get(field_name),
            code="REPLAY_METADATA_INCOMPLETE",
            context=f"{row.get('row_id', '<unknown>')}:{field_name}",
        )


def _validate_row_fields(row: dict[str, Any]) -> None:
    for field_name in REQUIRED_ROW_FIELDS:
        if field_name not in row:
            if field_name == "auth_lane":
                raise ValueError("AUTH_LANE_LABEL_REQUIRED")
            if field_name == "lane_status":
                raise ValueError("AUTH_LANE_STATUS_INVALID")
            raise ValueError(f"REQUIRED_ROW_FIELD_MISSING: {field_name}")
    for field_name in (
        "row_id",
        "proof_item_id",
        "call_id",
        "scenario_id",
        "entrypoint",
        "scenario_scope_note",
        "side_effect_assertion",
    ):
        _require_non_empty_string(
            row.get(field_name),
            code="REQUIRED_ROW_FIELD_MISSING",
            context=field_name,
        )
    _require_non_empty_string(row.get("evidence_ref"), code="EVIDENCE_REF_REQUIRED", context="evidence_ref")
    _validate_replay_metadata(row)


def _validate_row_values(row: dict[str, Any]) -> None:
    call_id = _require_non_empty_string(
        row.get("call_id"),
        code="REQUIRED_ROW_FIELD_MISSING",
        context="call_id",
    )
    if call_id not in LOCKED_REPRESENTATIVE_CALLS:
        raise ValueError(f"LOCKED_REPRESENTATIVE_SET_VIOLATION: {call_id}")

    proof_surface = row.get("proof_surface")
    if proof_surface not in ALLOWED_PROOF_SURFACES:
        raise ValueError(f"PROOF_SURFACE_INVALID: {proof_surface}")

    scenario_type = row.get("scenario_type")
    if scenario_type not in ALLOWED_SCENARIO_TYPES:
        raise ValueError(f"SCENARIO_TYPE_INVALID: {scenario_type}")

    auth_lane = row.get("auth_lane")
    if auth_lane not in ALLOWED_AUTH_LANES:
        raise ValueError(f"AUTH_LANE_LABEL_REQUIRED: {auth_lane}")
    lane_status = row.get("lane_status")
    if lane_status not in ALLOWED_LANE_STATUS:
        raise ValueError(f"AUTH_LANE_STATUS_INVALID: {lane_status}")

    if bool(row.get("protected_surface")) and auth_lane == "n/a":
        raise ValueError("AUTH_LANE_LABEL_REQUIRED: protected rows must name an auth lane")

    if lane_status == "skipped":
        _require_non_empty_string(
            row.get("skip_reason"),
            code="AUTH_LANE_SKIP_REASON_REQUIRED",
            context=str(row.get("row_id")),
        )

    result = row.get("result")
    if result not in ALLOWED_RESULTS:
        raise ValueError(f"RESULT_STATE_INVALID: {result}")

    if scenario_type == "negative":
        negative_case = row.get("negative_case")
        if not isinstance(negative_case, dict):
            raise ValueError("NEGATIVE_PAIRING_REQUIRED")
        if not negative_case.get("visible_block_asserted") or not negative_case.get("no_side_effect_asserted"):
            raise ValueError("NEGATIVE_PAIRING_REQUIRED")


def _validate_top_level(matrix: dict[str, Any]) -> list[dict[str, Any]]:
    for field_name in ("wf_id", "representative_call_lock", "proof_surface_enum", "closure_artifacts", "rows"):
        if field_name not in matrix:
            raise ValueError(f"MATRIX_FIELD_MISSING: {field_name}")
    if matrix.get("wf_id") != "WF-0072":
        raise ValueError("WF_ID_INVALID")
    if tuple(matrix.get("representative_call_lock", [])) != LOCKED_REPRESENTATIVE_CALLS:
        raise ValueError("LOCKED_REPRESENTATIVE_SET_INVALID")
    if set(matrix.get("proof_surface_enum", [])) != ALLOWED_PROOF_SURFACES:
        raise ValueError("PROOF_SURFACE_ENUM_INVALID")
    rows = matrix.get("rows")
    if not isinstance(rows, list):
        raise ValueError("ROWS_LIST_REQUIRED")
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"ROW_OBJECT_REQUIRED: index={index}")
    return rows


def _markdown_heading_to_anchor(line: str) -> str:
    heading = re.sub(r"^#+\s*", "", line.strip())
    heading = re.sub(r"[^\w\s-]", "", heading, flags=re.UNICODE).strip().lower()
    return re.sub(r"\s+", "-", heading)


def _validate_closure_ref_exists(ref: str, *, context: str) -> None:
    doc_path_text, anchor = ref.split("#", maxsplit=1)
    repo_root = Path(__file__).resolve().parents[2]
    doc_path = repo_root / doc_path_text
    if not doc_path.exists():
        raise ValueError(f"CLOSURE_ARTIFACT_REF_MISSING: {context}")
    text = doc_path.read_text(encoding="utf-8")
    anchor_candidates = {
        _markdown_heading_to_anchor(line)
        for line in text.splitlines()
        if line.lstrip().startswith("#")
    }
    if anchor not in anchor_candidates:
        raise ValueError(f"CLOSURE_ARTIFACT_ANCHOR_INVALID: {context}")


def _row_matches_required_item(row: dict[str, Any], required_row: str) -> bool:
    parts = required_row.split(":")
    if len(parts) < 2:
        raise ValueError(f"REQUIRED_ROW_FORMAT_INVALID: {required_row}")
    if row.get("call_id") != parts[0] or row.get("scenario_id") != parts[1]:
        return False
    if len(parts) == 2:
        return True
    scope = parts[2]
    return (
        row.get("auth_lane") == scope
        or row.get("scenario_variant") == scope
        or str(row.get("proof_item_id", "")).endswith(f":{scope}")
    )


def _validate_required_rows(rows: list[dict[str, Any]], required_rows: list[str]) -> None:
    for required_row in required_rows:
        if not any(_row_matches_required_item(row, required_row) for row in rows):
            raise ValueError(f"REQUIRED_ROW_MISSING: {required_row}")


def _validate_real_user_path(rows: list[dict[str, Any]]) -> None:
    expected_entrypoint = "/app -> /api/bff/structured-review"
    for row in rows:
        if bool(row.get("protected_surface")) and _require_non_empty_string(
            row.get("entrypoint"),
            code="ENTRYPOINT_REQUIRED",
            context="entrypoint",
        ) != expected_entrypoint:
            raise ValueError("REAL_USER_PATH_REQUIRED")


def _validate_protected_lane_parity(rows: list[dict[str, Any]]) -> None:
    lanes = ("test_bypass", "clerk")
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        entrypoint = str(row.get("entrypoint", ""))
        claims_protected_seam = bool(row.get("protected_surface")) or "/app" in entrypoint or "/api/bff/" in entrypoint
        if not claims_protected_seam:
            continue
        proof_item_id = _require_non_empty_string(
            row.get("proof_item_id"),
            code="REQUIRED_ROW_FIELD_MISSING",
            context="proof_item_id",
        )
        grouped.setdefault(proof_item_id, []).append(row)

    for proof_item_id, proof_rows in grouped.items():
        for lane in lanes:
            has_executed = any(
                row.get("auth_lane") == lane and row.get("lane_status") == "executed"
                for row in proof_rows
            )
            has_skip = any(
                row.get("auth_lane") == lane
                and row.get("lane_status") == "skipped"
                and isinstance(row.get("skip_reason"), str)
                and bool(row["skip_reason"].strip())
                for row in proof_rows
            )
            if not has_executed and not has_skip:
                raise ValueError(f"PROTECTED_LANE_PARITY_MISSING: {proof_item_id}:{lane}")


def _validate_closure(matrix: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    closure_artifacts = matrix.get("closure_artifacts")
    if not isinstance(closure_artifacts, dict):
        raise ValueError("CLOSURE_ARTIFACTS_REQUIRED")
    for field_name in ("baseline_scope_ref", "audit_disposition_ref"):
        value = _require_non_empty_string(
            closure_artifacts.get(field_name),
            code="CLOSURE_ARTIFACTS_REQUIRED",
            context=field_name,
        )
        if value.startswith("TBD"):
            raise ValueError(f"CLOSURE_ARTIFACTS_REQUIRED: {field_name}")
        if "/" not in value or "#" not in value:
            raise ValueError(f"CLOSURE_ARTIFACT_REF_INVALID: {field_name}")
        _validate_closure_ref_exists(value, context=field_name)

    for row in rows:
        if row.get("result") == "fail":
            raise ValueError(f"CLOSURE_ROWS_BLOCKED: {row.get('row_id')}")
        if row.get("lane_status") == "skipped":
            _require_non_empty_string(
                row.get("skip_reason"),
                code="CLOSURE_ROWS_BLOCKED",
                context=f"{row.get('row_id')}:skip_reason",
            )
    closure_status = matrix.get("closure_status")
    if not isinstance(closure_status, dict):
        raise ValueError("CLOSURE_STATUS_REQUIRED")
    rows_total = len(rows)
    rows_pass = sum(1 for row in rows if row.get("result") == "pass")
    rows_skip = sum(1 for row in rows if row.get("result") == "skip")
    rows_fail = sum(1 for row in rows if row.get("result") == "fail")
    if closure_status.get("matrix_result") != "pass":
        raise ValueError("CLOSURE_STATUS_INVALID: matrix_result")
    expected_counts = {
        "rows_total": rows_total,
        "rows_pass": rows_pass,
        "rows_skip_with_rationale": rows_skip,
        "rows_fail": rows_fail,
    }
    for field_name, expected_value in expected_counts.items():
        if closure_status.get(field_name) != expected_value:
            raise ValueError(f"CLOSURE_STATUS_MISMATCH: {field_name}")


def validate_matrix_payload(
    *,
    matrix: dict[str, Any],
    required_rows: list[str] | None = None,
    require_real_user_path: bool = False,
    require_protected_lanes: bool = False,
    require_closure: bool = False,
) -> None:
    rows = _validate_top_level(matrix)
    if not rows:
        raise ValueError("ROWS_REQUIRED")

    seen_row_ids: set[str] = set()
    for row in rows:
        _validate_row_fields(row)
        _validate_row_values(row)
        row_id = str(row["row_id"])
        if row_id in seen_row_ids:
            raise ValueError(f"DUPLICATE_ROW_ID: {row_id}")
        seen_row_ids.add(row_id)

    _validate_required_rows(rows, required_rows or [])

    if require_real_user_path:
        _validate_real_user_path(rows)
    if require_protected_lanes:
        _validate_protected_lane_parity(rows)
    if require_closure:
        _validate_protected_lane_parity(rows)
        _validate_closure(matrix, rows)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate WF-0072 verification matrix.")
    parser.add_argument("--matrix", required=True, type=Path, help="Path to verification-matrix.json")
    parser.add_argument("--require-row", action="append", default=[], help="Required row token call_id:scenario_id[:lane]")
    parser.add_argument(
        "--require-real-user-path",
        action="store_true",
        help="Require protected rows to use /app -> /api/bff/structured-review entrypoint.",
    )
    parser.add_argument(
        "--require-protected-lanes",
        action="store_true",
        help="Require protected proof items to cover both auth lanes or explicit skip reason.",
    )
    parser.add_argument(
        "--require-closure",
        action="store_true",
        help="Require protected-lane parity and closure artifact references.",
    )
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    matrix = _load_json_object(args.matrix)
    validate_matrix_payload(
        matrix=matrix,
        required_rows=args.require_row,
        require_real_user_path=args.require_real_user_path,
        require_protected_lanes=args.require_protected_lanes,
        require_closure=args.require_closure,
    )
    print("WF-0072 verification matrix validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
