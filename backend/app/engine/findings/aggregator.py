from __future__ import annotations

from dataclasses import replace

from app.engine.contracts import DiagnosticFindingV1
from app.engine.findings.check_catalog import apply_risk_taxonomy

_SEVERITY_RANK = {
    "ERROR": 3,
    "WARNING": 2,
    "NOTE": 1,
}


class FindingAggregationError(ValueError):
    def __init__(self, *, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


def _join_reasons_stably(reasons: list[str]) -> str:
    return " | ".join(sorted(set(reasons)))


def _source_priority(finding: DiagnosticFindingV1) -> int:
    return 1 if finding.finding_id.startswith("finding:obs:") else 0


def _merge_duplicate_findings(
    findings: list[DiagnosticFindingV1],
) -> list[DiagnosticFindingV1]:
    grouped: dict[tuple[str, str, str], list[DiagnosticFindingV1]] = {}
    for finding in findings:
        identity = (
            finding.primary_expectation_ref,
            finding.subject_ref.node_logical_id,
            finding.check_id,
        )
        grouped.setdefault(identity, []).append(finding)

    merged: list[DiagnosticFindingV1] = []
    for identity in sorted(grouped):
        duplicates = grouped[identity]
        winner = max(
            duplicates,
            key=lambda item: (
                _SEVERITY_RANK.get(item.severity, 0),
                -_source_priority(item),
                item.finding_id,
            ),
        )
        merged.append(
            replace(
                winner,
                reason=_join_reasons_stably([item.reason for item in duplicates]),
            )
        )
    return merged


def sort_key_for_finding(
    finding: DiagnosticFindingV1,
    expectation_order: dict[str, int],
) -> tuple[int, int, str]:
    return (
        -_SEVERITY_RANK.get(finding.severity, 0),
        expectation_order.get(finding.primary_expectation_ref, 10_000),
        finding.check_id,
    )


def aggregate_findings(
    *,
    findings: list[DiagnosticFindingV1],
    expectation_order: dict[str, int],
) -> list[DiagnosticFindingV1]:
    merged_findings = _merge_duplicate_findings(findings)
    findings_with_taxonomy = [apply_risk_taxonomy(finding) for finding in merged_findings]

    return sorted(
        findings_with_taxonomy,
        key=lambda item: sort_key_for_finding(item, expectation_order),
    )
