"""backend/tests/test_call_yaml_authoring_contract.py
Contract tests for call YAML authoring and governance docs.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.no_db


def test_wf0074_authoring_docs_fail_closed_on_subordinate_prompt_flattening() -> None:
    workflow_text = Path("../docs/call-yaml/authoring-workflow.md").read_text(
        encoding="utf-8"
    )
    checklist_text = Path("../docs/call-yaml/onboarding-checklist.md").read_text(
        encoding="utf-8"
    )
    workflow_text_lower = workflow_text.lower()
    checklist_text_lower = checklist_text.lower()

    assert (
        "subordinate official prompts/questions under an evaluation element must be preserved explicitly"
        in workflow_text
    )
    assert "existing flat canonical yamls remain temporarily compatible" in workflow_text_lower
    assert (
        "this wf does not widen the activated snapshot / engine contract seam beyond `schema_version` plus `expectations`"
        in workflow_text_lower
    )

    assert (
        "subordinate prompts were preserved or explicitly justified as absent by source"
        in checklist_text_lower
    )
    assert "existing flat canonical yamls remain temporarily compatible" in checklist_text_lower
    assert (
        "activated snapshot / engine contract seam remains limited to `schema_version` plus `expectations`"
        in checklist_text_lower
    )
