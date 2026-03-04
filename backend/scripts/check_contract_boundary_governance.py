from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import argparse

REQUEST_BOUNDARY_TRIGGER_CLASS = "request_boundary_contract_surface"
CONTRACT_GATE_SELECTOR_TRIGGER_CLASS = "contract_gate_selector_surface"
CI_CONTRACT_GATE_WIRING_TRIGGER_CLASS = "ci_contract_gate_wiring_surface"
WORKFLOW_TRACEABILITY_TRIGGER_CLASS = "workflow_traceability_surface"

TRIGGER_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        REQUEST_BOUNDARY_TRIGGER_CLASS,
        (
            "backend/app/engine/contracts.py",
            "backend/app/engine/review_request_validator.py",
        ),
    ),
    (
        CONTRACT_GATE_SELECTOR_TRIGGER_CLASS,
        (
            "backend/tests/engine/test_review_request_contracts.py",
            "backend/pyproject.toml",
        ),
    ),
    (
        CI_CONTRACT_GATE_WIRING_TRIGGER_CLASS,
        (".github/workflows/ci.yml",),
    ),
    (
        WORKFLOW_TRACEABILITY_TRIGGER_CLASS,
        (
            "docs/tasks/task-WF-0053-contract-boundary-governance-enforcement.md",
            "docs/walkthroughs/walkthrough-WF-0053-contract-boundary-governance-enforcement.md",
        ),
    ),
)

CONTRACT_GATE_EVIDENCE_BUNDLE_ID = "contract_gate_evidence"
ARTIFACT_TRACEABILITY_EVIDENCE_BUNDLE_ID = "artifact_traceability_evidence"
NEGATIVE_SMOKE_EVIDENCE_BUNDLE_ID = "negative_smoke_evidence"
MISSING_BUNDLES_REASON_CODE = "MISSING_REQUIRED_EVIDENCE_BUNDLES"
REQUIRED_BUNDLE_IDS: tuple[str, ...] = (
    CONTRACT_GATE_EVIDENCE_BUNDLE_ID,
    ARTIFACT_TRACEABILITY_EVIDENCE_BUNDLE_ID,
    NEGATIVE_SMOKE_EVIDENCE_BUNDLE_ID,
)


@dataclass(frozen=True)
class GovernanceResult:
    exit_code: int
    triggered_classes: list[str]
    missing_bundle_ids: list[str]
    reason_code: str
    message: str


def _path_matches_prefixes(path: str, prefixes: Sequence[str]) -> bool:
    return any(path.startswith(prefix) for prefix in prefixes)


def evaluate_governance(
    *,
    changed_paths: Sequence[str],
    evidence_bundle_ids: Sequence[str],
) -> GovernanceResult:
    triggered_classes = [
        trigger_class
        for trigger_class, prefixes in TRIGGER_RULES
        if any(_path_matches_prefixes(path, prefixes) for path in changed_paths)
    ]

    required_bundle_ids: set[str] = set()
    if triggered_classes:
        required_bundle_ids.update(REQUIRED_BUNDLE_IDS)

    provided_bundle_ids = set(evidence_bundle_ids)
    missing_bundle_ids = sorted(required_bundle_ids - provided_bundle_ids)

    if missing_bundle_ids:
        return GovernanceResult(
            exit_code=1,
            triggered_classes=triggered_classes,
            missing_bundle_ids=missing_bundle_ids,
            reason_code=MISSING_BUNDLES_REASON_CODE,
            message=_render_missing_bundle_diagnostic(missing_bundle_ids),
        )

    return GovernanceResult(
        exit_code=0,
        triggered_classes=triggered_classes,
        missing_bundle_ids=[],
        reason_code="GOVERNANCE_CHECK_OK",
        message="GOVERNANCE_CHECK_OK",
    )


def _render_missing_bundle_diagnostic(missing_bundle_ids: Sequence[str]) -> str:
    return f"{MISSING_BUNDLES_REASON_CODE}: {','.join(missing_bundle_ids)}"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fail-closed contract boundary governance checker",
    )
    parser.add_argument(
        "--changed-path",
        action="append",
        default=[],
        help="Changed path under governance evaluation.",
    )
    parser.add_argument(
        "--evidence-bundle",
        action="append",
        default=[],
        help="Evidence bundle ID present in this run.",
    )
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    result = evaluate_governance(
        changed_paths=args.changed_path,
        evidence_bundle_ids=args.evidence_bundle,
    )
    print(result.message)
    if result.triggered_classes:
        print("triggered_classes=" + ",".join(result.triggered_classes))
    if result.missing_bundle_ids:
        print("missing_bundle_ids=" + ",".join(result.missing_bundle_ids))
    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
