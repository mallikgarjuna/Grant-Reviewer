from __future__ import annotations

import hashlib

from app.engine.contracts import AnchorV1, ObservationV1, SubjectRef


def _stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _build_anchor(node_logical_id: str, node_text: str) -> AnchorV1:
    normalized_text = node_text.strip()
    locator_seed = f"{node_logical_id}|{len(normalized_text)}|{_stable_hash(normalized_text)}"
    locator = f"text-span:{_stable_hash(locator_seed)[:16]}"
    return AnchorV1(
        anchor_type="TEXT_SPAN",
        locator=locator,
        text_hash=_stable_hash(normalized_text),
    )


def extract_observations(
    call_config_snapshot: dict,
    proposal_nodes: dict[str, str],
) -> list[ObservationV1]:
    observations: list[ObservationV1] = []

    for node in call_config_snapshot.get("proposal_nodes", []):
        node_id = str(node["id"])
        node_text = proposal_nodes.get(node_id, "")
        anchor = _build_anchor(node_id, node_text)

        for node_expectation in node.get("node_expectations", []):
            expectation_ref = str(node_expectation["evaluation_element_id"])
            dependencies = [str(item) for item in node_expectation.get("dependencies", [])]
            missing_dependencies = [
                dependency
                for dependency in dependencies
                if not proposal_nodes.get(dependency, "").strip()
            ]

            if missing_dependencies:
                observations.append(
                    ObservationV1(
                        observation_id=(
                            f"obs:{node_id}:{expectation_ref}:dependency_missing"
                        ),
                        subject_ref=SubjectRef(node_logical_id=node_id),
                        expectation_ref=expectation_ref,
                        observation_kind="DEPENDENCY_CONTEXT_MISSING",
                        anchor=anchor,
                        details={"missing_dependencies": missing_dependencies},
                    )
                )
                continue

            observations.append(
                ObservationV1(
                    observation_id=f"obs:{node_id}:{expectation_ref}:present",
                    subject_ref=SubjectRef(node_logical_id=node_id),
                    expectation_ref=expectation_ref,
                    observation_kind="TEXT_PRESENT",
                    anchor=anchor,
                    details={"has_text": bool(node_text.strip())},
                )
            )

    return observations
