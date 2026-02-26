# WF-0033 — Data Contract Foundation Brainstorm

Artifact: brainstorm
Version: v0.3
Status: Draft Complete (Transitioning to PRD)
Last Updated: 2026-02-26

---

## 1. Problem Statement

Grant Reviewer is moving toward supporting complex, hierarchical grant structures (like ERC). The current API contracts are too rigid and "flat," forcing the frontend to hardcode structural knowledge for each funding program. This creates a maintenance bottleneck and prevents the realization of a "Universal Form Renderer."

### Brainstorming Q&A:

**Q1: What is the primary bottleneck for supporting ERC-style grants?**
- A) Database schema limitations.
- B) Rigid API contracts that do not natively support hierarchical structures.
- C) Lack of frontend components to render nested sections.
> Recommendation: B — The database already tracks `parent_node_id`, but the API flattens this data. Fixing the API contract is the highest-leverage move to unblock all consumers.
> **Selected: B**

**Q2: Why not just build the tree in the frontend from the flat list?**
- A) Performance concerns with large trees.
- B) Centralizing logic prevents duplication across multiple clients (Web, CLI, etc.).
- C) The current frontend architecture cannot handle asynchronous tree building.
> Recommendation: B — Moving this logic to the backend ensures a single source of truth for the grant's "canonical shape."
> **Selected: B**

---

## 2. Desired Outcome

The creation of a stable, metadata-driven "Data Contract" that allows the frontend to dynamically render any grant structure (from simple flat lists to multi-level ERC trees) without program-specific code.

### Brainstorming Q&A:

**Q1: What defines a successful "Data Contract"?**
- A) A single "God Endpoint" that returns structure and data in one payload.
- B) Decoupled routes for the "Structural Tree" and "Rich Metadata" (DTO).
- C) Auto-generating the entire frontend application from a YAML definition.
> Recommendation: B — Decoupling allows the UI to fetch the structural "skeleton" first for navigation, then fetch heavy metadata (constraints, guidance) only as needed.
> **Selected: B**

---

## 3. Target User / Actor

The primary beneficiary is the **Universal Form Renderer** (Frontend Component) and the developers maintaining it. By improving the DX (Developer Experience) of the API, we enable faster onboarding of new funding programs.

### Brainstorming Q&A:

**Q1: Who is the primary consumer of this new API contract?**
- A) Final grant applicants (End-users).
- B) Support staff / Admins.
- C) The Universal Form Renderer component.
> Recommendation: C — While end-users benefit ultimately, the immediate "customer" is the internal component architecture.
> **Selected: C**

---

## 4. Rough Idea Exploration

We will implement a recursive `children` structure in the `NodeSummary` DTO and introduce a new `Metadata DTO` route that bridges the gap between the internal `CallDefinitionV2` and the Needs of the UI.

### Brainstorming Q&A:

**Q1: How should we implement the tree-shaped response?**
- A) Introduce a new endpoint: `GET /calls/{id}/tree`.
- B) Add an optional `?nested=true` toggle to the existing `GET /calls/{id}/nodes`.
- C) Change the existing endpoint to always return nested results (breaking change).
> Recommendation: B — This provides the cleanest path for progressive migration of frontend components without a "big bang" breaking change.
> **Selected: B**

**Q2: Where should the Metadata DTO fetch its data?**
- A) Directly from raw YAML files on disk.
- B) From the `CallDefinition.canonical_json` column in the database.
- C) From a new dedicated metadata table.
> Recommendation: B — `canonical_json` already stores the validated V2 definition. It is the most robust and queryable source of truth.
> **Selected: B**

---

## 5. Constraints

The design must be strictly compatible with the existing `CallDefinitionV2` schema to avoid breaking the inhalation/compliance pipeline.

### Brainstorming Q&A:

**Q1: What is the most critical technical constraint?**
- A) Supporting infinite levels of nesting.
- B) Strict compatibility with `CallDefinitionV2` schema.
- C) Performance must be under 100ms.
> Recommendation: B — We must leverage the existing YAML engineering work. Re-inventing the metadata schema would cause massive rework in the compliance engine.
> **Selected: B**

---

## 6. Risks / Unknowns

The primary risk is a mismatch between the backend's representation of "Content Constraints" (e.g., word count rules) and the frontend form's ability to execute them.

### Brainstorming Q&A:

**Q1: What is the highest risk for this workflow?**
- A) Performance lag on recursive database queries.
- B) Frontend-Backend mismatch on constraint execution logic.
- C) Database migration failures.
> Recommendation: B — We need to ensure the DTO serves constraints in a "Frontend-Ready" format that doesn't require the UI to understand complex backend logic.
> **Selected: B**

---

## 7. MVP Definition

A backend that can serve a nested tree of nodes for any call and provide a rich Metadata DTO for at least one "Complex" call (e.g., ERC-2026-STG).

### Brainstorming Q&A:

**Q1: What is the bare minimum functional slice?**
- A) Full support for every funding agency.
- B) Nested `/nodes` support + Metadata DTO for a single call.
- C) A fully automated form generation tool.
> Recommendation: B — Focus on proving the *Contract* works for one complex case before scaling horizontally.
> **Selected: B**

---

## 8. Explicit Non-Goals

- Changing the underlying Database Schema (SQLModel).
- Modifying the AI Review/Compliance engine logic.
- Implementing the actual UI Form Renderer (that belongs to the frontend team, though we provide the contract).

### Brainstorming Q&A:

**Q1: What are we explicitly NOT doing in this workflow?**
- A) Modifying the core Compliance Engine.
- B) Rewriting the SQLModel domain models.
- C) Adding new LLM features.
> Recommendation: All of the above. This is strictly an API/Contract infrastructure task.
> **Selected: A, B, C**

---

## Repo Reality Snapshot (Read-Only) - 2026-02-26

1.  **Flat API Surface**: `GET /calls/{id}/nodes` (`backend/main.py:L416`) returns a `NodesResponse` containing a flat list of `NodeSummary` objects.
2.  **Missing Metadata**: Frontend gating relies on `GET /api/public/calls/{call_logical_id}/config`, which lacks rich hierarchy or constraint metadata.
3.  **Hydration Ready**: `CallDefinitionService.get_hydrated_nodes` already exists to merge YAML config with DB nodes.
4.  **V2 Alignment**: The project has migrated to `CallDefinitionV2` schemas for ingestion.
5.  **Hardcoded Form Logic**: The frontend is currently program-aware rather than metadata-aware.
