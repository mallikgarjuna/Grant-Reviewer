from __future__ import annotations

from dataclasses import fields

import pytest

from app.engine.contracts import DiagnosticFindingV1

pytestmark = pytest.mark.no_db


ALLOWED_TOP_LEVEL_FIELDS_V1 = {
    "finding_id",
    "primary_expectation_ref",
    "subject_ref",
    "check_id",
    "finding_kind",
    "severity",
    "assessment_status",
    "reason",
}


def _diagnostic_finding_top_level_field_names() -> set[str]:
    return {item.name for item in fields(DiagnosticFindingV1)}


def test_schema_top_level_fields_match_explicit_v1_allowlist() -> None:
    assert _diagnostic_finding_top_level_field_names() == ALLOWED_TOP_LEVEL_FIELDS_V1
