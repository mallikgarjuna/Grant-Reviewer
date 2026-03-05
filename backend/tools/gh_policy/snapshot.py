from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _slug(value: str) -> str:
    return value.replace("/", "__")


def build_snapshot_path(*, repo: str, branch: str, snapshot_dir: Path) -> Path:
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    filename = f"snapshot_{_slug(repo)}_{_slug(branch)}_{timestamp}.json"
    return snapshot_dir / filename


def write_snapshot(
    *,
    repo: str,
    branch: str,
    mechanism: str,
    live_policy_raw: Any,
    captured_from_endpoints: list[str],
    snapshot_dir: Path,
) -> Path:
    snapshot_path = build_snapshot_path(repo=repo, branch=branch, snapshot_dir=snapshot_dir)
    payload = {
        "mechanism": mechanism,
        "live_policy_raw": live_policy_raw,
        "captured_from_endpoints": captured_from_endpoints,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["snapshot_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return snapshot_path
