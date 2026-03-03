from __future__ import annotations

import hashlib

from app.engine.contracts import DiagnosticFindingV1, ReviewRequestV1


def _hash_text(value: str, *, salt: str) -> str:
    salted_value = f"{salt}|{value}"
    return hashlib.sha256(salted_value.encode("utf-8")).hexdigest()


def _count_by(values: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts


def build_pipeline_telemetry(
    *,
    request: ReviewRequestV1,
    findings: list[DiagnosticFindingV1],
    status: str,
    planned_stage_sequence: list[str],
    executed_stages: list[str],
) -> dict[str, object]:
    request_scope_salt = f"{request.call_config_digest}:{request.request_id}"
    redacted_nodes = {
        node_logical_id: {
            "text_hash": _hash_text(
                text.strip(),
                salt=request_scope_salt,
            ),
            "length": len(text.strip()),
        }
        for node_logical_id, text in sorted(request.proposal_nodes.items())
    }

    return {
        "run": {
            "request_id": request.request_id,
            "mode": request.mode,
            "stage_ref": request.stage_ref,
            "engine_path": "pipeline_v1",
            "status": status,
            "planned_stage_sequence": planned_stage_sequence,
            "executed_stages": executed_stages,
        },
        "counters": {
            "finding_kind": _count_by([finding.finding_kind for finding in findings]),
            "severity": _count_by([finding.severity for finding in findings]),
            "assessment_status": _count_by(
                [finding.assessment_status for finding in findings]
            ),
        },
        "redacted_nodes": redacted_nodes,
    }
