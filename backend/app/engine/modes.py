from __future__ import annotations

from app.engine.contracts import DiagnosticFindingV1, EngineMode


def project_findings_for_mode(
    *,
    findings: list[DiagnosticFindingV1],
    mode: EngineMode,
) -> list[DiagnosticFindingV1]:
    if mode == "DIAGNOSTIC":
        return list(findings)
    if mode == "STRICT":
        return [finding for finding in findings if finding.severity == "ERROR"]
    raise ValueError(f"Unsupported mode: {mode}")
