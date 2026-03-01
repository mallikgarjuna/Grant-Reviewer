#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _extract_card_signature(payload: dict[str, Any]) -> list[tuple[str, str, str]]:
    cards = payload.get("cards", [])
    if not isinstance(cards, list):
        return []

    signatures: list[tuple[str, str, str]] = []
    for card in cards:
        if not isinstance(card, dict):
            continue
        signatures.append(
            (
                str(card.get("node_logical_id", "")),
                str(card.get("node_expectation_id", "")),
                str(card.get("rating", "")),
            )
        )
    return signatures


def _extract_error_code(payload: dict[str, Any]) -> str:
    error = payload.get("error")
    if isinstance(error, dict):
        return str(error.get("code", ""))
    return ""


def compare_structured_runs(
    *,
    legacy_payload: dict[str, Any],
    pipeline_payload: dict[str, Any],
) -> dict[str, Any]:
    legacy_signature = _extract_card_signature(legacy_payload)
    pipeline_signature = _extract_card_signature(pipeline_payload)

    status_match = str(legacy_payload.get("status", "")) == str(
        pipeline_payload.get("status", "")
    )
    error_code_match = _extract_error_code(legacy_payload) == _extract_error_code(
        pipeline_payload
    )
    structural_parity = legacy_signature == pipeline_signature

    differences: list[str] = []
    if not structural_parity:
        differences.append("card_signature_mismatch")
    if not status_match:
        differences.append("status_mismatch")
    if not error_code_match:
        differences.append("error_code_mismatch")

    differences.sort()

    return {
        "checks": {
            "structural_parity": structural_parity,
            "status_match": status_match,
            "error_code_match": error_code_match,
        },
        "differences": differences,
        "legacy": {
            "status": str(legacy_payload.get("status", "")),
            "error_code": _extract_error_code(legacy_payload),
            "card_signature": legacy_signature,
        },
        "pipeline_v1": {
            "status": str(pipeline_payload.get("status", "")),
            "error_code": _extract_error_code(pipeline_payload),
            "card_signature": pipeline_signature,
        },
    }


def _load_payload(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected object payload in {path}")
    return payload


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare legacy vs pipeline_v1 structured-review payloads."
    )
    parser.add_argument("--legacy", type=Path, required=True, help="Legacy JSON payload path")
    parser.add_argument(
        "--pipeline",
        type=Path,
        required=True,
        help="Pipeline v1 JSON payload path",
    )
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    result = compare_structured_runs(
        legacy_payload=_load_payload(args.legacy),
        pipeline_payload=_load_payload(args.pipeline),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
