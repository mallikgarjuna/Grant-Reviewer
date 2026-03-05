from __future__ import annotations

from typing import Final, TypedDict

EVENT_SCOPE_PULL_REQUEST_ONLY: Final[str] = "pull_request_only"
EVENT_SCOPE_PUSH_SAFE: Final[str] = "push_safe"


class GovernedStep(TypedDict):
    check_id: str
    check_name: str
    event_scope: str


GOVERNED_STEPS: Final[list[GovernedStep]] = [
    {
        "check_id": "contract_boundary_governance_check",
        "check_name": "Contract Boundary Governance Check",
        "event_scope": EVENT_SCOPE_PULL_REQUEST_ONLY,
    },
    {
        "check_id": "wf0053_negative_smoke",
        "check_name": "WF-0053 Negative Smoke (Expected Fail-Closed)",
        "event_scope": EVENT_SCOPE_PULL_REQUEST_ONLY,
    },
    {
        "check_id": "contract_gate_marker",
        "check_name": "Contract Gate (Marker)",
        "event_scope": EVENT_SCOPE_PUSH_SAFE,
    },
    {
        "check_id": "pytest_no_db",
        "check_name": "Test (Pytest no_db)",
        "event_scope": EVENT_SCOPE_PUSH_SAFE,
    },
]
