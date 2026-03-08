"""backend/app/services/node_role_resolution.py
Shared node-role resolution helpers for split visibility/reviewability behavior.
"""

from __future__ import annotations

from typing import Any

from app.models.domain import CallDefinition


def resolve_supporting_node_logical_ids_for_primary_path(
    call_definition: CallDefinition | None,
) -> set[str]:
    """Return supporting node ids only when split visibility/reviewability is enabled."""
    if call_definition is None:
        return set()
    canonical_json = call_definition.canonical_json
    if not isinstance(canonical_json, dict):
        return set()

    return extract_supporting_node_ids_from_canonical_json(canonical_json)


def extract_supporting_node_ids_from_canonical_json(
    canonical_json: dict[str, Any],
) -> set[str]:
    """Resolve supporting node ids from canonical JSON under split opt-in."""
    runtime_config = canonical_json.get("runtime_config")
    if not isinstance(runtime_config, dict):
        return set()
    if runtime_config.get("split_visibility_reviewability_enabled") is not True:
        return set()

    proposal_nodes = canonical_json.get("proposal_nodes")
    if not isinstance(proposal_nodes, list):
        return set()

    supporting_ids: set[str] = set()
    for node in proposal_nodes:
        if not isinstance(node, dict):
            continue
        node_id = node.get("id")
        if not isinstance(node_id, str) or not node_id.strip():
            continue
        if node.get("node_role") == "SUPPORTING":
            supporting_ids.add(node_id)
    return supporting_ids
