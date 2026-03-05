from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def build_evidence_payload(payload: dict[str, Any]) -> dict[str, Any]:
    payload_copy = dict(payload)
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
