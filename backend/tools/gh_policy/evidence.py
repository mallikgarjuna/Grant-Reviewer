from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any


_STABLE_ERROR_KIND_MAP = {
    "permission_denied": "permission_denied",
    "plan_gated": "plan_gated",
    "missing_required_checks": "missing_required_checks",
    "api_unreachable": "api_failure",
    "api_error": "api_failure",
    "api_failure": "api_failure",
}


def _normalize_error_payload(raw_error: Any) -> dict[str, Any]:
    if not isinstance(raw_error, dict):
        return {"kind": None, "message": None, "endpoint": None}

    kind = raw_error.get("kind")
    normalized_kind = _STABLE_ERROR_KIND_MAP.get(str(kind), kind) if kind is not None else None
    return {
        "kind": normalized_kind,
        "message": raw_error.get("message"),
        "endpoint": raw_error.get("endpoint"),
    }


def build_evidence_payload(payload: dict[str, Any]) -> dict[str, Any]:
    payload_copy = dict(payload)
    payload_copy["error"] = _normalize_error_payload(payload_copy.get("error"))
    payload_copy.setdefault("workflow_run_id", os.getenv("GITHUB_RUN_ID") or None)
    payload_copy.setdefault("commit_sha", os.getenv("GITHUB_SHA") or None)
    payload_copy.setdefault("linked_artifacts", None)

    canonical = json.dumps(payload_copy, sort_keys=True, separators=(",", ":"))
    payload_copy["evidence_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return payload_copy


def write_evidence_json(*, payload: dict[str, Any], output_path: Path) -> Path:
    finalized_payload = build_evidence_payload(payload)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(finalized_payload, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return output_path
