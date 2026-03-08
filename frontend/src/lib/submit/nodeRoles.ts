// frontend/src/lib/submit/nodeRoles.ts
import type { CallConfigResponse, NodeSummary } from "@/lib/bff/types";

type Role = "PRIMARY" | "SUPPORTING";

export type NodeRoleClassification = {
  role: Role;
  isPrimary: boolean;
  isSupporting: boolean;
  isContainer: boolean;
  isPrimarySubmittable: boolean;
};

export function isSplitVisibilityReviewabilityEnabled(
  callConfig: Pick<CallConfigResponse, "split_visibility_reviewability_enabled"> | null,
): boolean {
  return callConfig?.split_visibility_reviewability_enabled === true;
}

export function classifyNodeRole(
  node: Pick<NodeSummary, "node_role" | "has_expectations" | "node_type">,
  options: { splitVisibilityReviewabilityEnabled: boolean },
): NodeRoleClassification {
  const role: Role = options.splitVisibilityReviewabilityEnabled
    ? node.node_role === "SUPPORTING"
      ? "SUPPORTING"
      : "PRIMARY"
    : node.has_expectations
      ? "PRIMARY"
      : "SUPPORTING";

  const isContainer = node.has_expectations === false && node.node_type === "SECTION";
  const isPrimary = role === "PRIMARY";
  const isSupporting = role === "SUPPORTING";
  const isPrimarySubmittable = isPrimary && !isContainer;

  return {
    role,
    isPrimary,
    isSupporting,
    isContainer,
    isPrimarySubmittable,
  };
}
