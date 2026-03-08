// frontend/src/lib/submit/renderModel.test.ts
import { describe, expect, it } from "vitest";

import type { NodeSummary } from "@/lib/bff/types";
import { buildRenderModel } from "@/lib/submit/renderModel";

function wf0059ProofTargetNestedNodes(): NodeSummary[] {
  return [
    {
      id: "erc-stg-b1",
      logical_id: "b1",
      title: "Part B1",
      parent_node_id: null,
      node_type: "SECTION",
      order_index: 1,
      has_expectations: true,
    },
    {
      id: "erc-stg-b1-part1",
      logical_id: "b1_part1_scientific_proposal",
      title: "Part I of the Scientific Proposal",
      parent_node_id: "erc-stg-b1",
      node_type: "SUBSECTION",
      order_index: 2,
      has_expectations: true,
    },
  ];
}

function wf0059VeniControlNodes(): NodeSummary[] {
  return [
    {
      id: "veni-academic-profile",
      logical_id: "academic_profile",
      title: "Academic profile",
      parent_node_id: null,
      node_type: "SECTION",
      order_index: 1,
      has_expectations: true,
    },
    {
      id: "veni-key-outputs",
      logical_id: "key_outputs",
      title: "Key outputs",
      parent_node_id: null,
      node_type: "SECTION",
      order_index: 2,
      has_expectations: true,
    },
  ];
}

describe("buildRenderModel", () => {
  it("wf0059_render_model_proof_target_guard", () => {
    const proofTargetResult = buildRenderModel({
      nodes: wf0059ProofTargetNestedNodes(),
      metadataByLogicalId: {},
    });

    expect(proofTargetResult.state).toBe("unsupported");
    if (proofTargetResult.state !== "unsupported") {
      return;
    }
    expect(proofTargetResult.reason).toBe("nested_nodes");

    const veniControlResult = buildRenderModel({
      nodes: wf0059VeniControlNodes(),
      metadataByLogicalId: {},
    });

    expect(veniControlResult.state).toBe("ready");
    if (veniControlResult.state !== "ready") {
      return;
    }
    expect(veniControlResult.nodes.map((node) => node.nodeLogicalId)).toEqual([
      "academic_profile",
      "key_outputs",
    ]);
  });

  it("returns unsupported for nested node structures", () => {
    const result = buildRenderModel({
      nodes: [
        {
          id: "node-1",
          logical_id: "section_1",
          title: "Section 1",
          parent_node_id: null,
          node_type: "SECTION",
          order_index: 1,
          has_expectations: true,
        },
        {
          id: "node-2",
          logical_id: "section_1_child",
          title: "Section 1.1",
          parent_node_id: "node-1",
          node_type: "SUBSECTION",
          order_index: 2,
          has_expectations: true,
        },
      ],
      metadataByLogicalId: {},
    });

    expect(result.state).toBe("unsupported");
    if (result.state !== "unsupported") {
      return;
    }
    expect(result.reason).toBe("nested_nodes");
  });

  it("returns contract_error when any node logical_id is missing", () => {
    const result = buildRenderModel({
      nodes: [
        {
          id: "node-1",
          logical_id: null,
          title: "Section 1",
          parent_node_id: null,
          node_type: "SECTION",
          order_index: 1,
          has_expectations: true,
        },
      ],
      metadataByLogicalId: {},
    });

    expect(result.state).toBe("contract_error");
    if (result.state !== "contract_error") {
      return;
    }
    expect(result.reason).toBe("missing_logical_id");
  });

  it("keeps node logical_id identity while using metadata fallback labels", () => {
    const result = buildRenderModel({
      nodes: [
        {
          id: "node-a",
          logical_id: "academic_profile",
          title: "Academic Profile from Nodes",
          parent_node_id: null,
          node_type: "SECTION",
          order_index: 2,
          has_expectations: true,
        },
        {
          id: "node-b",
          logical_id: "research_idea",
          title: "Research Idea from Nodes",
          parent_node_id: null,
          node_type: "SECTION",
          order_index: 1,
          has_expectations: true,
        },
      ],
      metadataByLogicalId: {
        academic_profile: {
          title: "Academic Profile from Metadata",
        },
        not_present_in_nodes: {
          title: "Should never become a field",
        },
      },
    });

    expect(result.state).toBe("ready");
    if (result.state !== "ready") {
      return;
    }

    expect(result.nodes.map((item) => item.nodeLogicalId)).toEqual([
      "academic_profile",
      "research_idea",
    ]);
    expect(result.nodes.map((item) => item.label)).toEqual([
      "Academic Profile from Metadata",
      "Research Idea from Nodes",
    ]);
  });

  it("appends normalized source section numbering when available", () => {
    const result = buildRenderModel({
      nodes: [
        {
          id: "node-1",
          logical_id: "scientific_summary",
          title: "Scientific summary",
          parent_node_id: null,
          node_type: "SECTION",
          order_index: 1,
          has_expectations: true,
        },
        {
          id: "node-2",
          logical_id: "research_proposal",
          title: "Description of proposed research",
          parent_node_id: null,
          node_type: "SECTION",
          order_index: 2,
          has_expectations: true,
        },
      ],
      metadataByLogicalId: {
        scientific_summary: {
          title: "Scientific summary",
          sourceSection: "1b",
        },
        research_proposal: {
          title: "Description of proposed research",
          sourceSection: "2.a",
        },
      },
    });

    expect(result.state).toBe("ready");
    if (result.state !== "ready") {
      return;
    }

    expect(result.nodes.map((item) => item.label)).toEqual([
      "Scientific summary (1.b)",
      "Description of proposed research (2.a)",
    ]);
  });

  it("wf0060_render_model_excludes_structural_containers_from_submittable_nodes", () => {
    const result = buildRenderModel({
      nodes: [
        {
          id: "node-part-a",
          logical_id: "part_a",
          title: "Part A",
          parent_node_id: null,
          node_type: "SECTION",
          order_index: 1,
          has_expectations: false,
        },
        {
          id: "node-budget",
          logical_id: "budget",
          title: "Budget",
          parent_node_id: "node-part-a",
          node_type: "SECTION",
          order_index: 2,
          has_expectations: false,
        },
        {
          id: "node-resources",
          logical_id: "resources_time_commitment",
          title: "Resources and Time Commitment",
          parent_node_id: "node-budget",
          node_type: "SECTION",
          order_index: 3,
          has_expectations: true,
        },
        {
          id: "node-part-b",
          logical_id: "part_b",
          title: "Part B",
          parent_node_id: null,
          node_type: "SECTION",
          order_index: 4,
          has_expectations: false,
        },
        {
          id: "node-b1",
          logical_id: "b1",
          title: "Part B1",
          parent_node_id: "node-part-b",
          node_type: "SECTION",
          order_index: 5,
          has_expectations: false,
        },
        {
          id: "node-summary",
          logical_id: "proposal_summary",
          title: "Proposal Summary",
          parent_node_id: "node-b1",
          node_type: "SUBSECTION",
          order_index: 6,
          has_expectations: true,
        },
      ],
      metadataByLogicalId: {},
    });

    expect(result.state).toBe("ready");
    if (result.state !== "ready") {
      return;
    }
    expect(result.nodes.map((node) => node.nodeLogicalId)).toEqual([
      "resources_time_commitment",
      "proposal_summary",
    ]);
    expect(result.groups.map((group) => group.groupLabel)).toEqual([
      "Part A / Budget",
      "Part B / Part B1",
    ]);
  });

  it("wf0063_render_model_uses_node_role_for_opted_in_visibility", () => {
    const result = buildRenderModel({
      nodes: [
        {
          id: "node-part-b",
          logical_id: "part_b",
          title: "Part B",
          parent_node_id: null,
          node_type: "SECTION",
          order_index: 1,
          has_expectations: false,
          node_role: "SUPPORTING",
        },
        {
          id: "node-abstract",
          logical_id: "abstract",
          title: "Abstract",
          parent_node_id: "node-part-b",
          node_type: "SUBSECTION",
          order_index: 2,
          has_expectations: false,
          node_role: "SUPPORTING",
        },
        {
          id: "node-excellence",
          logical_id: "excellence",
          title: "Excellence",
          parent_node_id: "node-part-b",
          node_type: "SUBSECTION",
          order_index: 3,
          has_expectations: true,
          node_role: "PRIMARY",
        },
      ],
      metadataByLogicalId: {},
      splitVisibilityReviewabilityEnabled: true,
    });

    expect(result.state).toBe("ready");
    if (result.state !== "ready") {
      return;
    }
    expect(result.nodes.map((node) => node.nodeLogicalId)).toEqual([
      "abstract",
      "excellence",
    ]);
    expect(result.nodes.map((node) => node.nodeRole)).toEqual([
      "SUPPORTING",
      "PRIMARY",
    ]);
  });

  it("wf0063_render_model_preserves_legacy_nested_fallback_without_opt_in", () => {
    const result = buildRenderModel({
      nodes: [
        {
          id: "node-part-b",
          logical_id: "part_b",
          title: "Part B",
          parent_node_id: null,
          node_type: "SECTION",
          order_index: 1,
          has_expectations: false,
          node_role: "SUPPORTING",
        },
        {
          id: "node-abstract",
          logical_id: "abstract",
          title: "Abstract",
          parent_node_id: "node-part-b",
          node_type: "SUBSECTION",
          order_index: 2,
          has_expectations: false,
          node_role: "SUPPORTING",
        },
        {
          id: "node-excellence",
          logical_id: "excellence",
          title: "Excellence",
          parent_node_id: "node-part-b",
          node_type: "SUBSECTION",
          order_index: 3,
          has_expectations: true,
          node_role: "PRIMARY",
        },
      ],
      metadataByLogicalId: {},
      splitVisibilityReviewabilityEnabled: false,
    });

    expect(result.state).toBe("ready");
    if (result.state !== "ready") {
      return;
    }
    expect(result.nodes.map((node) => node.nodeLogicalId)).toEqual(["excellence"]);
  });
});
