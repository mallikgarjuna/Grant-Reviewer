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


def build_replay_artifact(
    *,
    legacy_payload: dict[str, Any],
    pipeline_payload: dict[str, Any],
    replays: int,
) -> dict[str, Any]:
    if replays < 1:
        raise ValueError("replays must be >= 1")

    runs: list[dict[str, Any]] = []
    structural_passes = 0
    status_passes = 0
    error_code_passes = 0

    for run_index in range(1, replays + 1):
        comparison = compare_structured_runs(
            legacy_payload=legacy_payload,
            pipeline_payload=pipeline_payload,
        )
        runs.append({"run_index": run_index, "comparison": comparison})
        if comparison["checks"]["structural_parity"]:
            structural_passes += 1
        if comparison["checks"]["status_match"]:
            status_passes += 1
        if comparison["checks"]["error_code_match"]:
            error_code_passes += 1

    return {
        "meta": {
            "artifact_type": "structured_rollout_replay_v1",
            "replays": replays,
        },
        "summary": {
            "total_runs": replays,
            "structural_parity_passes": structural_passes,
            "status_match_passes": status_passes,
            "error_code_match_passes": error_code_passes,
        },
        "runs": runs,
    }


def _load_payload(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected object payload in {path}")
    return payload


def write_json_deterministic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _default_payload_pair() -> tuple[dict[str, Any], dict[str, Any]]:
    payload = {
        "status": "COMPLETED",
        "cards": [
            {
                "node_logical_id": "academic_profile",
                "node_expectation_id": "exp-1",
                "rating": "NOTE",
            }
        ],
    }
    return payload, payload


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare legacy vs pipeline_v1 structured-review payloads."
    )
    parser.add_argument("--legacy", type=Path, help="Legacy JSON payload path")
    parser.add_argument(
        "--pipeline",
        type=Path,
        help="Pipeline v1 JSON payload path",
    )
    parser.add_argument(
        "--replays",
        type=int,
        default=1,
        help="Number of comparator runs to execute (default: 1)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional output artifact JSON path",
    )
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    if bool(args.legacy) != bool(args.pipeline):
        raise ValueError("Provide both --legacy and --pipeline, or neither.")

    if args.legacy and args.pipeline:
        legacy_payload = _load_payload(args.legacy)
        pipeline_payload = _load_payload(args.pipeline)
    else:
        legacy_payload, pipeline_payload = _default_payload_pair()

    artifact = build_replay_artifact(
        legacy_payload=legacy_payload,
        pipeline_payload=pipeline_payload,
        replays=args.replays,
    )
    if args.output:
        write_json_deterministic(args.output, artifact)
        print(f"Wrote replay artifact: {args.output}")
    else:
        print(json.dumps(artifact, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
