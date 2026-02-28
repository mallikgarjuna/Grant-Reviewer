import { describe, expect, it } from "vitest";

import { buildRenderModel } from "@/lib/submit/renderModel";

describe("buildRenderModel", () => {
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
});
