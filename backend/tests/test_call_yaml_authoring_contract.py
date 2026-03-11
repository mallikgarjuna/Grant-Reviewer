"""backend/tests/test_call_yaml_authoring_contract.py
Contract tests for call YAML authoring and governance docs.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.no_db

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _assert_contains_all(text: str, required_fragments: tuple[str, ...]) -> None:
    for fragment in required_fragments:
        assert fragment in text


def test_wf0074_authoring_docs_fail_closed_on_subordinate_prompt_flattening() -> None:
    workflow_text = (_REPO_ROOT / "docs/call-yaml/authoring-workflow.md").read_text(
        encoding="utf-8"
    )
    checklist_text = (_REPO_ROOT / "docs/call-yaml/onboarding-checklist.md").read_text(
        encoding="utf-8"
    )
    workflow_text_lower = workflow_text.lower()
    checklist_text_lower = checklist_text.lower()

    _assert_contains_all(
        workflow_text_lower,
        (
            "subordinate official prompts/questions",
            "must be preserved explicitly",
            "`subordinate_prompts`",
            "flattening them into summary prose is a contract violation",
        ),
    )
    _assert_contains_all(
        workflow_text_lower,
        (
            "existing flat canonical yamls remain temporarily compatible",
            "new or re-authored call",
            "typed structure",
        ),
    )
    _assert_contains_all(
        workflow_text_lower,
        (
            "does not widen the activated snapshot / engine contract seam",
            "`schema_version` plus `expectations`",
            "do not, by themselves, prove structured-review runtime consumption",
        ),
    )

    _assert_contains_all(
        checklist_text_lower,
        (
            "subordinate prompts were preserved",
            "explicitly justified as absent by source",
        ),
    )
    _assert_contains_all(
        checklist_text_lower,
        (
            "existing flat canonical yamls remain temporarily compatible",
            "does not apply to new or re-authored calls",
        ),
    )
    _assert_contains_all(
        checklist_text_lower,
        (
            "activated snapshot / engine contract seam remains limited",
            "`schema_version` plus `expectations`",
            "do not claim runtime-consumption impact",
        ),
    )


def test_wf0074_durable_governance_records_fidelity_policy_and_closure_gate() -> None:
    decisions_text = (_REPO_ROOT / "docs/logs/decisions.md").read_text(encoding="utf-8")
    project_docs_text = (_REPO_ROOT / "docs/memory/domain/project_docs.md").read_text(
        encoding="utf-8"
    )
    decisions_text_lower = decisions_text.lower()
    project_docs_text_lower = project_docs_text.lower()

    _assert_contains_all(
        decisions_text_lower,
        (
            "subordinate-prompt fidelity rule",
            "existing flat canonical yamls remain temporarily compatible",
            "no runtime-consumption claim",
        ),
    )
    assert "erc_poc_2026_full.yaml" in decisions_text

    _assert_contains_all(
        project_docs_text_lower,
        (
            "wf-0074 planning/execution must preserve durable decision/memory guidance",
            "audit-disposition closure",
            "no proceed or ship recommendation",
        ),
    )
    assert "`pass`/`fail`/`skipped` evidence" in project_docs_text
