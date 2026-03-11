"""backend/tests/test_call_yaml_authoring_contract.py
Contract tests for call YAML authoring and governance docs.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.no_db

_REPO_ROOT = Path(__file__).resolve().parents[2]


def test_wf0074_authoring_docs_fail_closed_on_subordinate_prompt_flattening() -> None:
    workflow_text = (_REPO_ROOT / "docs/call-yaml/authoring-workflow.md").read_text(
        encoding="utf-8"
    )
    checklist_text = (_REPO_ROOT / "docs/call-yaml/onboarding-checklist.md").read_text(
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


def test_wf0074_durable_governance_records_fidelity_policy_and_closure_gate() -> None:
    decisions_text = (_REPO_ROOT / "docs/logs/decisions.md").read_text(encoding="utf-8")
    project_docs_text = (_REPO_ROOT / "docs/memory/domain/project_docs.md").read_text(
        encoding="utf-8"
    )
    decisions_text_lower = decisions_text.lower()
    project_docs_text_lower = project_docs_text.lower()

    assert "subordinate-prompt fidelity rule" in decisions_text_lower
    assert "existing flat canonical yamls remain temporarily compatible" in decisions_text_lower
    assert "erc_poc_2026_full.yaml" in decisions_text
    assert "no runtime-consumption claim" in decisions_text_lower

    assert "wf-0074 planning/execution must preserve durable decision/memory guidance" in project_docs_text_lower
    assert "`pass`/`fail`/`skipped` evidence" in project_docs_text
    assert "audit-disposition closure" in project_docs_text_lower
    assert "no proceed or ship recommendation" in project_docs_text_lower
