from __future__ import annotations

from dataclasses import replace

from app.engine.contracts import DiagnosticFindingV1

ALLOWED_CHECK_IDS = {
    "check.presence",
    "check.dependency.context_missing",
    "check.expectation.satisfied",
}

RISK_TAXONOMY_CONTEXT_GAP = "RISK_CONTEXT_GAP"
RISK_TAXONOMY_REQUIRED_GAP = "RISK_REQUIRED_GAP"
RISK_TAXONOMY_QUALITY_CONCERN = "RISK_QUALITY_CONCERN"
RISK_TAXONOMY_INFORMATIONAL = "RISK_INFORMATIONAL"


def classify_risk_taxonomy(finding: DiagnosticFindingV1) -> str:
    if finding.assessment_status == "NOT_ASSESSABLE":
        return RISK_TAXONOMY_CONTEXT_GAP
    if finding.severity == "ERROR":
        return RISK_TAXONOMY_REQUIRED_GAP
    if finding.severity == "WARNING":
        return RISK_TAXONOMY_QUALITY_CONCERN
    return RISK_TAXONOMY_INFORMATIONAL


def apply_risk_taxonomy(finding: DiagnosticFindingV1) -> DiagnosticFindingV1:
    taxonomy = classify_risk_taxonomy(finding)
    if finding.risk_taxonomy is not None:
        return finding
    return replace(
        finding,
        risk_taxonomy=taxonomy,
    )
