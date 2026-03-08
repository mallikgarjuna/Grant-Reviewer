// frontend/src/lib/submit/nodeRoles.test.ts
import { describe, expect, it } from "vitest";

import {
  classifyCallNodeRoles,
  classifyNodeRole,
  isSplitVisibilityReviewabilityEnabled,
} from "@/lib/submit/nodeRoles";

describe("nodeRoles", () => {
  it("wf0063_node_role_helper_uses_backend_contract_without_call_specific_allowlists", () => {
    const optedInSupporting = classifyNodeRole(
      {
        node_role: "SUPPORTING",
        has_expectations: false,
        node_type: "SECTION",
      },
      { splitVisibilityReviewabilityEnabled: true, hasChildren: true },
    );
    expect(optedInSupporting.role).toBe("SUPPORTING");
    expect(optedInSupporting.isContainer).toBe(true);
    expect(optedInSupporting.isPrimarySubmittable).toBe(false);

    const optedInPrimary = classifyNodeRole(
      {
        node_role: "PRIMARY",
        has_expectations: true,
        node_type: "SECTION",
      },
      { splitVisibilityReviewabilityEnabled: true },
    );
    expect(optedInPrimary.role).toBe("PRIMARY");
    expect(optedInPrimary.isPrimarySubmittable).toBe(true);

    const legacyFallback = classifyNodeRole(
      {
        node_role: null,
        has_expectations: false,
        node_type: "SECTION",
      },
      { splitVisibilityReviewabilityEnabled: false },
    );
    expect(legacyFallback.role).toBe("SUPPORTING");
    expect(legacyFallback.isSupporting).toBe(true);
  });

  it("resolves split visibility opt-in from backend config field", () => {
    expect(
      isSplitVisibilityReviewabilityEnabled({
        split_visibility_reviewability_enabled: true,
      }),
    ).toBe(true);
    expect(
      isSplitVisibilityReviewabilityEnabled({
        split_visibility_reviewability_enabled: false,
      }),
    ).toBe(false);
    expect(isSplitVisibilityReviewabilityEnabled(null)).toBe(false);
  });

  it("wf0064_node_roles_support_review_detail_classification_without_new_helper", () => {
    const classification = classifyCallNodeRoles(
      [
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
      { splitVisibilityReviewabilityEnabled: true },
    );

    expect(classification.primarySubmittableNodeLogicalIds).toEqual(["excellence"]);
    expect(classification.visibleSupportingNodeLogicalIds).toEqual(["abstract"]);
    expect(classification.structuralContainerNodeLogicalIds).toEqual(["part_b"]);
  });
});
