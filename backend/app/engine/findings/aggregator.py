from __future__ import annotations

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
    findings_with_taxonomy = [apply_risk_taxonomy(finding) for finding in findings]
    seen_identity: set[tuple[str, str, str]] = set()
    for finding in findings_with_taxonomy:
        identity = (
            finding.primary_expectation_ref,
            finding.subject_ref.node_logical_id,
            finding.check_id,
        )
        if identity in seen_identity:
            raise FindingAggregationError(
                code="DUPLICATE_FINDING_IDENTITY",
                message=f"Duplicate finding identity: {identity}",
            )
        seen_identity.add(identity)

    return sorted(
        findings_with_taxonomy,
        key=lambda item: sort_key_for_finding(item, expectation_order),
    )
