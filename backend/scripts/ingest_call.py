"""
Ingestion script for Admin Call Definition as Code.

Reads a YAML file conforming to CallDefinition schema and performs
atomic, idempotent upsert into the database.

Usage:
    uv run scripts/ingest_call.py <path/to/call.yaml> [--dry-run]
"""

import argparse
import hashlib
import json
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import yaml
from pydantic import ValidationError
from sqlmodel import Session, select

# Add backend to path for imports (per lessons.md L1)
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.domain import (
    CallDefinition as CallDefinitionRecord,
)
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
    CallDefinition as CallDefinitionV1,
)
from app.schemas.call_definitions import (
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


def _format_validation_error(err: ValidationError, schema_version: str) -> str:
    """Render concise validation errors with field paths."""
    details: list[str] = []
    for entry in err.errors():
        loc = ".".join(str(item) for item in entry["loc"])
        msg = entry["msg"]
        details.append(f"{loc}: {msg}")

    joined = "\n  - ".join(details)
    return (
        f"Schema validation failed for {schema_version}:\n  - {joined}"
        if details
        else f"Schema validation failed for {schema_version}"
    )


def _format_yaml_syntax_error(err: yaml.YAMLError, path: Path, raw_text: str) -> str:
    """Render actionable YAML syntax errors with location context."""
    message = [f"YAML syntax error in {path}"]
    mark = getattr(err, "problem_mark", None)
    if mark is not None:
        line = mark.line + 1
        column = mark.column + 1
        message.append(f"at line {line}, column {column}")

        lines = raw_text.splitlines()
        if 0 <= mark.line < len(lines):
            source_line = lines[mark.line]
            message.append(f"  {source_line}")
            message.append(f"  {' ' * mark.column}^")

    problem = getattr(err, "problem", None)
    if problem:
        message.append(str(problem))

    return ": ".join(message)


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


def load_yaml(path: Path) -> tuple[str, CallDefinitionV1 | CallDefinitionV2, str]:
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
        raw_text = f.read()

    try:
        loaded = yaml.safe_load(raw_text)
    except yaml.YAMLError as err:
        raise ValueError(_format_yaml_syntax_error(err, path, raw_text)) from err

    if not isinstance(loaded, dict):
        raise ValueError("YAML root must be a mapping/object")

    raw_data: dict[str, Any] = loaded

    schema_version = _detect_schema_version(raw_data)
    try:
        if schema_version == "v1":
            call_def = CallDefinitionV1.model_validate(raw_data)
        else:
            call_def = CallDefinitionV2.model_validate(raw_data)
    except ValidationError as err:
        raise ValueError(_format_validation_error(err, schema_version)) from err

    logger.info(f"YAML validated successfully (schema_version={schema_version})")
    return schema_version, call_def, raw_text


# ============================================================================
# ID Mapping
# ============================================================================
def resolve_logical_ids(call_def: CallDefinitionV1) -> dict[str, UUID]:
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


def _build_v1_dry_run_summary(
    call_def: CallDefinitionV1,
    yaml_path: Path,
) -> dict[str, Any]:
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
    canonical_json, canonical_json_text = _build_canonical_json(call_def)
    checksum = _compute_semantic_checksum(canonical_json_text)
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
        "checksum": checksum,
        "canonical_json": canonical_json,
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
        "compliance_rules": {
            "by_severity": dict(sorted(compliance_by_severity.items()))
        },
        "runtime_notes": {"count": len(call_def.runtime_notes)},
    }


def _build_canonical_json(call_def: CallDefinitionV2) -> tuple[dict[str, Any], str]:
    """Create deterministic canonical JSON payload and encoded text."""
    canonical_json = call_def.model_dump(exclude_none=True)
    canonical_json_text = json.dumps(
        canonical_json,
        sort_keys=True,
        separators=(",", ":"),
    )
    return canonical_json, canonical_json_text


def _compute_semantic_checksum(canonical_json_text: str) -> str:
    """Compute deterministic SHA-256 checksum for canonical JSON payload."""
    return hashlib.sha256(canonical_json_text.encode("utf-8")).hexdigest()


# ============================================================================
# Ingestion Functions
# ============================================================================
def ingest_agency_and_call(
    session: Session,
    call_def: CallDefinitionV1,
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
                EvaluationCriterion.archived_at.is_(None),
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
                    EvaluationElement.archived_at.is_(None),
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
            ProposalNode.archived_at.is_(None),
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
# V2 Ingestion Functions
# ============================================================================
def _map_v2_node_type(node_type: str) -> NodeType:
    """Map V2 node type labels to existing NodeType enum."""
    if node_type.upper() == "SUBSECTION":
        return NodeType.SUBSECTION
    return NodeType.SECTION


def _upsert_agency_and_call_v2(
    session: Session,
    call_def: CallDefinitionV2,
) -> tuple[FundingAgency, FundingCall]:
    """Upsert FundingAgency/FundingCall metadata for V2 ingestion."""
    agency_def = call_def.funding_agency
    call_meta = call_def.funding_call

    agency = session.exec(
        select(FundingAgency).where(FundingAgency.short_name == agency_def.id)
    ).first()
    if agency is None:
        agency = FundingAgency(
            name=agency_def.name,
            short_name=agency_def.id,
            description=f"Country: {agency_def.country}",
        )
        session.add(agency)
        session.flush()
    else:
        agency.name = agency_def.name
        agency.description = f"Country: {agency_def.country}"
        session.add(agency)

    call = session.exec(
        select(FundingCall).where(FundingCall.code == call_meta.code)
    ).first()
    if call is None:
        call = FundingCall(
            funding_agency_id=agency.id,
            name=call_meta.title,
            code=call_meta.code,
            call_year=call_meta.year,
            general_guidelines=f"Stage={call_meta.stage}; Language={call_meta.language}",
        )
        session.add(call)
        session.flush()
    else:
        call.funding_agency_id = agency.id
        call.name = call_meta.title
        call.call_year = call_meta.year
        call.general_guidelines = (
            f"Stage={call_meta.stage}; Language={call_meta.language}"
        )
        session.add(call)

    return agency, call


def _upsert_call_definition_document(
    session: Session,
    *,
    funding_call_id: UUID,
    schema_version: str,
    checksum: str,
    raw_yaml: str,
    canonical_json: dict[str, Any],
    source_path: str,
) -> CallDefinitionRecord:
    """Insert/update canonical call-definition JSON document."""
    now = datetime.now(UTC)
    existing = session.exec(
        select(CallDefinitionRecord).where(
            CallDefinitionRecord.funding_call_id == funding_call_id
        )
    ).first()
    if existing is None:
        record = CallDefinitionRecord(
            funding_call_id=funding_call_id,
            schema_version=schema_version,
            checksum=checksum,
            raw_yaml=raw_yaml,
            canonical_json=canonical_json,
            source_path=source_path,
            created_at=now,
            updated_at=now,
        )
        session.add(record)
        return record

    existing.schema_version = schema_version
    existing.checksum = checksum
    existing.raw_yaml = raw_yaml
    existing.canonical_json = canonical_json
    existing.source_path = source_path
    existing.updated_at = now
    session.add(existing)
    return existing


def _upsert_projection_v2(
    session: Session,
    *,
    call_id: UUID,
    call_def: CallDefinitionV2,
) -> dict[str, int]:
    """Upsert nodes/criteria/elements by logical_id and soft-delete orphaned rows."""
    now = datetime.now(UTC)
    counters = {
        "criteria_upserted": 0,
        "elements_upserted": 0,
        "nodes_upserted": 0,
        "criteria_archived": 0,
        "elements_archived": 0,
        "nodes_archived": 0,
        "expectations_replaced": 0,
    }

    existing_criteria = {
        criterion.logical_id: criterion
        for criterion in session.exec(
            select(EvaluationCriterion).where(
                EvaluationCriterion.funding_call_id == call_id,
                EvaluationCriterion.archived_at.is_(None),
            )
        ).all()
        if criterion.logical_id is not None
    }
    seen_criteria: set[str] = set()
    criterion_by_logical_id: dict[str, EvaluationCriterion] = {}
    for order_idx, criterion_def in enumerate(call_def.evaluation_criteria, start=1):
        criterion_description = f"stage={criterion_def.stage}; weight_percent={criterion_def.weight_percent}"
        criterion = existing_criteria.get(criterion_def.id)
        if criterion is None:
            criterion = EvaluationCriterion(
                funding_call_id=call_id,
                logical_id=criterion_def.id,
                name=criterion_def.name,
                description=criterion_description,
                order_index=order_idx,
                archived_at=None,
            )
            session.add(criterion)
        else:
            criterion.logical_id = criterion_def.id
            criterion.name = criterion_def.name
            criterion.description = criterion_description
            criterion.order_index = order_idx
            criterion.archived_at = None
            session.add(criterion)
        counters["criteria_upserted"] += 1
        seen_criteria.add(criterion_def.id)
        criterion_by_logical_id[criterion_def.id] = criterion

    for criterion in existing_criteria.values():
        if criterion.logical_id not in seen_criteria:
            criterion.archived_at = now
            session.add(criterion)
            counters["criteria_archived"] += 1

    session.flush()

    existing_elements = {
        element.logical_id: element
        for element in session.exec(
            select(EvaluationElement)
            .join(
                EvaluationCriterion,
                EvaluationElement.evaluation_criterion_id == EvaluationCriterion.id,
            )
            .where(EvaluationCriterion.funding_call_id == call_id)
            .where(EvaluationCriterion.archived_at.is_(None))
            .where(EvaluationElement.archived_at.is_(None))
        ).all()
        if element.logical_id is not None
    }
    seen_elements: set[str] = set()
    element_uuid_by_logical_id: dict[str, UUID] = {}
    for criterion_def in call_def.evaluation_criteria:
        criterion = criterion_by_logical_id[criterion_def.id]
        for element_def in criterion_def.evaluation_elements:
            element = existing_elements.get(element_def.id)
            if element is None:
                element = EvaluationElement(
                    evaluation_criterion_id=criterion.id,
                    logical_id=element_def.id,
                    name=element_def.name,
                    description=element_def.description,
                    archived_at=None,
                )
                session.add(element)
            else:
                element.evaluation_criterion_id = criterion.id
                element.logical_id = element_def.id
                element.name = element_def.name
                element.description = element_def.description
                element.archived_at = None
                session.add(element)
            counters["elements_upserted"] += 1
            seen_elements.add(element_def.id)
            session.flush()
            element_uuid_by_logical_id[element_def.id] = element.id

    for element in existing_elements.values():
        if element.logical_id not in seen_elements:
            element.archived_at = now
            session.add(element)
            counters["elements_archived"] += 1

    existing_nodes = {
        node.logical_id: node
        for node in session.exec(
            select(ProposalNode).where(
                ProposalNode.funding_call_id == call_id,
                ProposalNode.archived_at.is_(None),
            )
        ).all()
        if node.logical_id is not None
    }
    seen_nodes: set[str] = set()
    node_by_logical_id: dict[str, ProposalNode] = {}
    for order_idx, node_def in enumerate(call_def.proposal_nodes, start=1):
        node = existing_nodes.get(node_def.id)
        if node is None:
            node = ProposalNode(
                funding_call_id=call_id,
                parent_node_id=None,
                logical_id=node_def.id,
                node_type=_map_v2_node_type(node_def.node_type),
                title=node_def.label,
                order_index=order_idx,
                guidance_text=node_def.guidance_text,
                archived_at=None,
            )
            session.add(node)
        else:
            node.parent_node_id = None
            node.logical_id = node_def.id
            node.node_type = _map_v2_node_type(node_def.node_type)
            node.title = node_def.label
            node.order_index = order_idx
            node.guidance_text = node_def.guidance_text
            node.archived_at = None
            session.add(node)
        counters["nodes_upserted"] += 1
        seen_nodes.add(node_def.id)
        session.flush()
        node_by_logical_id[node_def.id] = node

    for node in existing_nodes.values():
        if node.logical_id not in seen_nodes:
            node.archived_at = now
            session.add(node)
            counters["nodes_archived"] += 1

    for node in node_by_logical_id.values():
        existing_expectations = session.exec(
            select(NodeExpectation).where(NodeExpectation.proposal_node_id == node.id)
        ).all()
        counters["expectations_replaced"] += len(existing_expectations)
        for expectation in existing_expectations:
            session.delete(expectation)

    for node_def in call_def.proposal_nodes:
        node = node_by_logical_id[node_def.id]
        for order_idx, expectation_def in enumerate(
            node_def.node_expectations, start=1
        ):
            element_id = element_uuid_by_logical_id.get(
                expectation_def.evaluation_element_id
            )
            if element_id is None:
                raise ValueError(
                    "Missing evaluation element during expectation projection: "
                    f"{expectation_def.evaluation_element_id}"
                )
            session.add(
                NodeExpectation(
                    proposal_node_id=node.id,
                    evaluation_element_id=element_id,
                    expectation_strength=ExpectationStrength(
                        expectation_def.expectation_strength
                    ),
                    evaluation_intent=EvaluationIntent(
                        expectation_def.evaluation_intent
                    ),
                    guidance_note=expectation_def.guidance_note,
                    order_index=order_idx,
                )
            )
            counters["expectations_replaced"] += 1

    return counters


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
    schema_version, call_def, raw_yaml = load_yaml(yaml_path)

    if dry_run:
        logger.info("=== DRY RUN MODE - No database changes will be made ===")
        if schema_version == "v1":
            return _build_v1_dry_run_summary(call_def, yaml_path)

        return _build_v2_dry_run_summary(call_def, yaml_path)

    # Import DB wiring only for non-dry-run execution.
    from app.db import create_db_and_tables, get_session

    # Initialize database
    create_db_and_tables()
    session = get_session()

    try:
        if schema_version == "v1":
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
        else:
            v2_call_def = call_def
            canonical_json, canonical_json_text = _build_canonical_json(v2_call_def)
            checksum = _compute_semantic_checksum(canonical_json_text)

            with session.begin():
                agency, call = _upsert_agency_and_call_v2(session, v2_call_def)
                existing_definition = session.exec(
                    select(CallDefinitionRecord).where(
                        CallDefinitionRecord.funding_call_id == call.id
                    )
                ).first()
                if existing_definition and existing_definition.checksum == checksum:
                    return {
                        "dry_run": False,
                        "schema_version": "v2",
                        "skipped": True,
                        "reason": "checksum_match",
                        "call_id": str(call.id),
                        "checksum": checksum,
                    }

                _upsert_call_definition_document(
                    session,
                    funding_call_id=call.id,
                    schema_version="v2",
                    checksum=checksum,
                    raw_yaml=raw_yaml,
                    canonical_json=canonical_json,
                    source_path=str(yaml_path),
                )
                counters = _upsert_projection_v2(
                    session,
                    call_id=call.id,
                    call_def=v2_call_def,
                )

            result = {
                "dry_run": False,
                "schema_version": "v2",
                "skipped": False,
                "agency_id": str(agency.id),
                "call_id": str(call.id),
                "checksum": checksum,
                **counters,
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
            logger.info(
                "Dry-run summary:\n%s", json.dumps(result, indent=2, sort_keys=True)
            )
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
