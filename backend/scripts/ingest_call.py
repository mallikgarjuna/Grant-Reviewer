"""
Ingestion script for Admin Call Definition as Code.

Reads a YAML file conforming to CallDefinition schema and performs
atomic, idempotent upsert into the database.

Usage:
    uv run scripts/ingest_call.py <path/to/call.yaml> [--dry-run]
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import yaml
from sqlmodel import Session, select

# Add backend to path for imports (per lessons.md L1)
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.domain import (
    EvaluationCriterion,
    EvaluationElement,
    EvaluationIntent,
    ExpectationStrength,
    FundingAgency,
    FundingCall,
    NodeExpectation,
    NodeType,
    ProposalNode,
)
from app.schemas.call_definitions import (
    CallDefinition,
    EvaluationCriterionDefinition,
    NodeExpectationDefinition,
    ProposalNodeDefinition,
)
from app.schemas.call_definitions_v2 import CallDefinitionV2

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ============================================================================
# Load & Parse
# ============================================================================
def _detect_schema_version(raw_data: dict[str, Any]) -> str:
    """Detect call-definition schema version from funding_agency keys."""
    funding_agency = raw_data.get("funding_agency")
    if not isinstance(funding_agency, dict):
        raise ValueError("Missing or invalid 'funding_agency' object in YAML")

    has_v1_key = "short_name" in funding_agency
    has_v2_key = "id" in funding_agency

    if has_v1_key and has_v2_key:
        raise ValueError(
            "Ambiguous schema version: 'funding_agency' contains both "
            "'short_name' (v1) and 'id' (v2). Keep only one."
        )
    if has_v1_key:
        return "v1"
    if has_v2_key:
        return "v2"
    raise ValueError(
        "Unable to detect schema version: funding_agency must contain either "
        "'short_name' (v1) or 'id' (v2)."
    )


def load_yaml(path: Path) -> tuple[str, CallDefinition | CallDefinitionV2]:
    """
    Load and validate a YAML file into a CallDefinition.

    Args:
        path: Path to the YAML file.

    Returns:
        Tuple of (schema_version, validated call definition instance).

    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If validation fails.
    """
    if not path.exists():
        raise FileNotFoundError(f"YAML file not found: {path}")

    logger.info(f"Loading YAML from: {path}")

    with open(path, encoding="utf-8") as f:
        raw_data: dict[str, Any] = yaml.safe_load(f)

    schema_version = _detect_schema_version(raw_data)
    if schema_version == "v1":
        call_def = CallDefinition.model_validate(raw_data)
    else:
        call_def = CallDefinitionV2.model_validate(raw_data)

    logger.info(f"YAML validated successfully (schema_version={schema_version})")
    return schema_version, call_def


# ============================================================================
# ID Mapping
# ============================================================================
def resolve_logical_ids(call_def: CallDefinition) -> dict[str, UUID]:
    """
    Create a mapping from logical string IDs to UUIDs.

    This pre-generates UUIDs for all criteria and elements defined in the YAML,
    allowing NodeExpectations to reference them during ingestion.

    Args:
        call_def: Validated CallDefinition.

    Returns:
        Dictionary mapping logical IDs to UUIDs.
    """
    id_map: dict[str, UUID] = {}

    for criterion in call_def.evaluation_criteria:
        id_map[criterion.id] = uuid4()
        for element in criterion.evaluation_elements:
            id_map[element.id] = uuid4()

    logger.info(f"Resolved {len(id_map)} logical IDs to UUIDs")
    return id_map


def _build_v1_dry_run_summary(call_def: CallDefinition, yaml_path: Path) -> dict[str, Any]:
    """Build deterministic dry-run summary for V1 call definitions."""
    return {
        "dry_run": True,
        "schema_version": "v1",
        "source_path": str(yaml_path),
        "funding_agency": {
            "short_name": call_def.funding_agency.short_name,
            "name": call_def.funding_agency.name,
        },
        "funding_call": {
            "code": call_def.funding_call.code,
            "name": call_def.funding_call.name,
            "year": call_def.funding_call.year,
        },
        "evaluation_criteria": {
            "count": len(call_def.evaluation_criteria),
            "items": [
                {
                    "id": criterion.id,
                    "name": criterion.name,
                    "evaluation_elements_count": len(criterion.evaluation_elements),
                }
                for criterion in call_def.evaluation_criteria
            ],
        },
        "proposal_nodes": {"count": _count_nodes(call_def.proposal_nodes)},
    }


def _build_v2_dry_run_summary(
    call_def: CallDefinitionV2,
    yaml_path: Path,
) -> dict[str, Any]:
    """Build deterministic dry-run summary for V2 call definitions."""
    compliance_by_severity: dict[str, int] = {}
    for node in call_def.proposal_nodes:
        for rule in node.compliance_rules:
            compliance_by_severity[rule.severity] = (
                compliance_by_severity.get(rule.severity, 0) + 1
            )

    return {
        "dry_run": True,
        "schema_version": "v2",
        "source_path": str(yaml_path),
        "funding_agency": {
            "id": call_def.funding_agency.id,
            "name": call_def.funding_agency.name,
        },
        "funding_call": {
            "id": call_def.funding_call.id,
            "code": call_def.funding_call.code,
            "title": call_def.funding_call.title,
            "year": call_def.funding_call.year,
            "stage": call_def.funding_call.stage,
        },
        "evaluation_criteria": {
            "count": len(call_def.evaluation_criteria),
            "items": [
                {
                    "id": criterion.id,
                    "name": criterion.name,
                    "weight_percent": criterion.weight_percent,
                    "evaluation_elements_count": len(criterion.evaluation_elements),
                }
                for criterion in call_def.evaluation_criteria
            ],
        },
        "proposal_nodes": {
            "count": len(call_def.proposal_nodes),
            "items": [
                {
                    "id": node.id,
                    "label": node.label,
                    "node_type": node.node_type,
                    "constraints": (
                        node.content_constraints.model_dump(exclude_none=True)
                        if node.content_constraints
                        else {}
                    ),
                }
                for node in call_def.proposal_nodes
            ],
        },
        "compliance_rules": {"by_severity": dict(sorted(compliance_by_severity.items()))},
        "runtime_notes": {"count": len(call_def.runtime_notes)},
    }


# ============================================================================
# Ingestion Functions
# ============================================================================
def ingest_agency_and_call(
    session: Session,
    call_def: CallDefinition,
) -> tuple[FundingAgency, FundingCall]:
    """
    Upsert FundingAgency and FundingCall.

    Uses short_name (agency) and code (call) as natural business keys.

    Args:
        session: Database session.
        call_def: Validated CallDefinition.

    Returns:
        Tuple of (FundingAgency, FundingCall).
    """
    agency_def = call_def.funding_agency
    call_meta = call_def.funding_call

    # Upsert Agency by short_name
    existing_agency = session.exec(
        select(FundingAgency).where(FundingAgency.short_name == agency_def.short_name)
    ).first()

    if existing_agency:
        logger.info(f"Agency '{agency_def.short_name}' exists, updating metadata")
        existing_agency.name = agency_def.name
        existing_agency.description = agency_def.description
        agency = existing_agency
    else:
        logger.info(f"Creating new agency: {agency_def.short_name}")
        agency = FundingAgency(
            name=agency_def.name,
            short_name=agency_def.short_name,
            description=agency_def.description,
        )
        session.add(agency)

    session.commit()
    session.refresh(agency)

    # Upsert Call by code
    existing_call = session.exec(
        select(FundingCall).where(FundingCall.code == call_meta.code)
    ).first()

    if existing_call:
        logger.info(f"Call '{call_meta.code}' exists, updating metadata")
        existing_call.name = call_meta.name
        existing_call.call_year = call_meta.year
        existing_call.aim_objectives = call_meta.aim_objectives
        existing_call.scope = call_meta.scope
        existing_call.general_guidelines = call_meta.general_guidelines
        call = existing_call
    else:
        logger.info(f"Creating new call: {call_meta.code}")
        call = FundingCall(
            funding_agency_id=agency.id,
            name=call_meta.name,
            code=call_meta.code,
            call_year=call_meta.year,
            aim_objectives=call_meta.aim_objectives,
            scope=call_meta.scope,
            general_guidelines=call_meta.general_guidelines,
        )
        session.add(call)

    session.commit()
    session.refresh(call)
    return agency, call


def ingest_rubric(
    session: Session,
    call_id: UUID,
    rubric_def: list[EvaluationCriterionDefinition],
    id_map: dict[str, UUID],
) -> None:
    """
    Upsert EvaluationCriteria and EvaluationElements.

    Uses the pre-generated UUID from id_map for new records.
    For existing records, matches by name within the call.

    Args:
        session: Database session.
        call_id: UUID of the FundingCall.
        rubric_def: List of criteria definitions.
        id_map: Logical ID to UUID mapping.
    """
    for order_idx, crit_def in enumerate(rubric_def, start=1):
        # Check if criterion exists by name within this call
        existing_crit = session.exec(
            select(EvaluationCriterion).where(
                EvaluationCriterion.funding_call_id == call_id,
                EvaluationCriterion.name == crit_def.name,
            )
        ).first()

        if existing_crit:
            logger.info(f"Criterion '{crit_def.name}' exists, updating")
            existing_crit.description = crit_def.description
            existing_crit.order_index = order_idx
            criterion = existing_crit
            # Update id_map with the existing DB ID
            id_map[crit_def.id] = criterion.id
        else:
            logger.info(f"Creating criterion: {crit_def.name}")
            criterion = EvaluationCriterion(
                id=id_map[crit_def.id],
                funding_call_id=call_id,
                name=crit_def.name,
                description=crit_def.description,
                order_index=order_idx,
            )
            session.add(criterion)

        session.commit()
        session.refresh(criterion)

        # Process elements
        for elem_def in crit_def.evaluation_elements:
            existing_elem = session.exec(
                select(EvaluationElement).where(
                    EvaluationElement.evaluation_criterion_id == criterion.id,
                    EvaluationElement.name == elem_def.name,
                )
            ).first()

            if existing_elem:
                logger.info(f"  Element '{elem_def.name}' exists, updating")
                existing_elem.description = elem_def.description
                # Update id_map with the existing DB ID
                id_map[elem_def.id] = existing_elem.id
            else:
                logger.info(f"  Creating element: {elem_def.name}")
                element = EvaluationElement(
                    id=id_map[elem_def.id],
                    evaluation_criterion_id=criterion.id,
                    name=elem_def.name,
                    description=elem_def.description,
                )
                session.add(element)

        session.commit()


def ingest_nodes_recursive(
    session: Session,
    call_id: UUID,
    nodes: list[ProposalNodeDefinition],
    parent_id: UUID | None,
    id_map: dict[str, UUID],
) -> None:
    """
    Recursively upsert ProposalNodes and their NodeExpectations.

    For existing nodes (matched by title + parent), expectations are replaced.
    New nodes are created with fresh UUIDs.

    Args:
        session: Database session.
        call_id: UUID of the FundingCall.
        nodes: List of node definitions at this level.
        parent_id: UUID of parent node (None for root).
        id_map: Logical ID to UUID mapping (for elements).
    """
    for order_idx, node_def in enumerate(nodes, start=1):
        # Match by title and parent within this call
        query = select(ProposalNode).where(
            ProposalNode.funding_call_id == call_id,
            ProposalNode.title == node_def.title,
        )
        if parent_id is None:
            # NOTE: Use is_(None) instead of == None for SQL NULL comparisons.
            # In SQL, you must use "IS NULL" not "= NULL". SQLAlchemy's is_()
            # method generates the correct "WHERE column IS NULL" clause.
            query = query.where(ProposalNode.parent_node_id.is_(None))
        else:
            query = query.where(ProposalNode.parent_node_id == parent_id)

        existing_node = session.exec(query).first()

        if existing_node:
            logger.info(f"Node '{node_def.title}' exists, updating")
            existing_node.node_type = NodeType(node_def.node_type)
            existing_node.guidance_text = node_def.guidance_text
            existing_node.order_index = order_idx
            node = existing_node
        else:
            logger.info(f"Creating node: {node_def.title}")
            node = ProposalNode(
                funding_call_id=call_id,
                parent_node_id=parent_id,
                node_type=NodeType(node_def.node_type),
                title=node_def.title,
                order_index=order_idx,
                guidance_text=node_def.guidance_text,
            )
            session.add(node)

        session.commit()
        session.refresh(node)

        # Replace expectations for this node (delete existing, insert from YAML)
        _replace_expectations(session, node.id, node_def.node_expectations, id_map)

        # Recurse for children
        if node_def.children:
            ingest_nodes_recursive(session, call_id, node_def.children, node.id, id_map)


def _replace_expectations(
    session: Session,
    node_id: UUID,
    expectations: list[NodeExpectationDefinition],
    id_map: dict[str, UUID],
) -> None:
    """
    Replace all NodeExpectations for a given node.

    This allows removing expectations by omitting them from the YAML.

    Args:
        session: Database session.
        node_id: UUID of the ProposalNode.
        expectations: List of expectation definitions.
        id_map: Logical ID to UUID mapping for elements.
    """
    # Delete existing expectations for this node
    existing = session.exec(
        select(NodeExpectation).where(NodeExpectation.proposal_node_id == node_id)
    ).all()

    if existing:
        logger.info(f"  Deleting {len(existing)} existing expectations")
        for exp in existing:
            session.delete(exp)
        session.commit()

    # Insert new expectations from YAML
    for order_idx, exp_def in enumerate(expectations, start=1):
        element_uuid = id_map.get(exp_def.evaluation_element_id)
        if not element_uuid:
            raise ValueError(
                f"Element ID '{exp_def.evaluation_element_id}' not found in id_map. "
                "This should not happen if schema validation passed."
            )

        logger.info(f"  Adding expectation: {exp_def.evaluation_element_id}")
        expectation = NodeExpectation(
            proposal_node_id=node_id,
            evaluation_element_id=element_uuid,
            expectation_strength=ExpectationStrength(exp_def.expectation_strength),
            evaluation_intent=EvaluationIntent(exp_def.evaluation_intent),
            guidance_note=exp_def.guidance_note,
            order_index=order_idx,
        )
        session.add(expectation)

    session.commit()


# ============================================================================
# Main Ingestion Pipeline
# ============================================================================
def ingest_call(yaml_path: Path, dry_run: bool = False) -> dict[str, Any]:
    """
    Main ingestion pipeline.

    Args:
        yaml_path: Path to the YAML call definition.
        dry_run: If True, validate and log but don't commit changes.

    Returns:
        Summary dictionary with ingested IDs.
    """
    # Load and validate
    schema_version, call_def = load_yaml(yaml_path)

    if dry_run:
        logger.info("=== DRY RUN MODE - No database changes will be made ===")
        if schema_version == "v1":
            return _build_v1_dry_run_summary(call_def, yaml_path)

        return _build_v2_dry_run_summary(call_def, yaml_path)

    if schema_version != "v1":
        raise ValueError(
            "V2 call-definition ingestion is currently supported in --dry-run only."
        )

    # Import DB wiring only for non-dry-run execution.
    from app.db import create_db_and_tables, get_session

    # Initialize database
    create_db_and_tables()
    session = get_session()

    try:
        # Resolve logical IDs
        v1_call_def = call_def
        id_map = resolve_logical_ids(v1_call_def)

        # Ingest in order
        agency, call = ingest_agency_and_call(session, v1_call_def)

        ingest_rubric(session, call.id, v1_call_def.evaluation_criteria, id_map)

        ingest_nodes_recursive(
            session,
            call.id,
            v1_call_def.proposal_nodes,
            None,
            id_map,
        )

        logger.info("=== Ingestion completed successfully ===")

        # Capture result IDs before closing session (per lessons.md L2)
        result = {
            "dry_run": False,
            "schema_version": "v1",
            "agency_id": str(agency.id),
            "call_id": str(call.id),
            "criteria_count": len(v1_call_def.evaluation_criteria),
            "node_count": _count_nodes(v1_call_def.proposal_nodes),
        }

    finally:
        session.close()

    return result


def _count_nodes(nodes: list[ProposalNodeDefinition]) -> int:
    """Recursively count total nodes."""
    count = len(nodes)
    for node in nodes:
        count += _count_nodes(node.children)
    return count


# ============================================================================
# CLI Entry Point
# ============================================================================
def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Ingest a YAML call definition into the database."
    )
    parser.add_argument(
        "yaml_file",
        type=Path,
        help="Path to the YAML call definition file",
    )
    # NOTE: argparse converts dashes to underscores for attribute names.
    # So --dry-run becomes args.dry_run in Python. This is standard behavior.
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and preview without committing to database",
    )
    args = parser.parse_args()

    try:
        result = ingest_call(args.yaml_file, args.dry_run)
        if args.dry_run:
            logger.info("Dry-run summary:\n%s", json.dumps(result, indent=2, sort_keys=True))
        logger.info(f"Result: {result}")
    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
