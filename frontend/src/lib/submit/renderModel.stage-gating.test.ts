// frontend/src/lib/submit/renderModel.stage-gating.test.ts
// WF-0070 Task 8: Verify frontend stage-eligible ERC leaf display
// and isNodeEligibleForStage correctness for authoritative stage contract.

import { describe, expect, it } from "vitest";

import { isNodeEligibleForStage, type RenderNode } from "@/lib/submit/renderModel";

function makeNode(overrides: Partial<RenderNode>): RenderNode {
  return {
    id: "node-1",
    nodeLogicalId: "test_node",
    label: "Test Node",
    reviewStage: "BOTH",
    nodeRole: "PRIMARY",
    ...overrides,
  };
}

describe("isNodeEligibleForStage – WF-0070 stage gating", () => {
  it("wf0070_t8_step_2_only_node_hidden_in_step_1", () => {
    const b2Node = makeNode({
      nodeLogicalId: "b2_part2_scientific_proposal",
      reviewStage: "STEP_2",
    });

    expect(isNodeEligibleForStage(b2Node, "STEP_1")).toBe(false);
    expect(isNodeEligibleForStage(b2Node, "STEP_2")).toBe(true);
  });

  it("wf0070_t8_resources_node_hidden_in_step_1", () => {
    const resourcesNode = makeNode({
      nodeLogicalId: "resources_time_commitment",
      reviewStage: "STEP_2",
    });

    expect(isNodeEligibleForStage(resourcesNode, "STEP_1")).toBe(false);
    expect(isNodeEligibleForStage(resourcesNode, "STEP_2")).toBe(true);
  });

  it("wf0070_t8_both_stage_node_visible_in_both_steps", () => {
    const summaryNode = makeNode({
      nodeLogicalId: "proposal_summary",
      reviewStage: "BOTH",
    });

    expect(isNodeEligibleForStage(summaryNode, "STEP_1")).toBe(true);
    expect(isNodeEligibleForStage(summaryNode, "STEP_2")).toBe(true);
  });

  it("wf0070_t8_step_1_only_node_hidden_in_step_2", () => {
    // Hypothetical STEP_1-only node (not currently in ERC, but tests the logic)
    const step1Node = makeNode({
      nodeLogicalId: "hypothetical_step1_only",
      reviewStage: "STEP_1",
    });

    expect(isNodeEligibleForStage(step1Node, "STEP_1")).toBe(true);
    expect(isNodeEligibleForStage(step1Node, "STEP_2")).toBe(false);
  });

  it("wf0070_t8_review_stage_passthrough_not_coerced", () => {
    // Ensures the function doesn't coerce "STEP_2" to "STEP_1" or vice versa
    const b2Node = makeNode({ reviewStage: "STEP_2" });
    // If the function coerced, it would return true for STEP_1 too
    expect(isNodeEligibleForStage(b2Node, "STEP_1")).toBe(false);
  });
});
