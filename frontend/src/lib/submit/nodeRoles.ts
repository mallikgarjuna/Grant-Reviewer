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

export type CallNodeRoleSummary = {
  byLogicalId: Map<string, NodeRoleClassification>;
  primarySubmittableNodeLogicalIds: string[];
  visibleSupportingNodeLogicalIds: string[];
  structuralContainerNodeLogicalIds: string[];
};

export function isSplitVisibilityReviewabilityEnabled(
  callConfig: Pick<CallConfigResponse, "split_visibility_reviewability_enabled"> | null,
): boolean {
  return callConfig?.split_visibility_reviewability_enabled === true;
}

export function classifyNodeRole(
  node: Pick<NodeSummary, "node_role" | "has_expectations" | "node_type">,
  options: {
    splitVisibilityReviewabilityEnabled: boolean;
    hasChildren?: boolean;
  },
): NodeRoleClassification {
  const role: Role = options.splitVisibilityReviewabilityEnabled
    ? node.node_role === "SUPPORTING"
      ? "SUPPORTING"
      : "PRIMARY"
    : node.has_expectations
      ? "PRIMARY"
      : "SUPPORTING";

  const isContainer = node.has_expectations === false && options.hasChildren === true;
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

export function classifyCallNodeRoles(
  nodes: Array<
    Pick<
      NodeSummary,
      "id" | "logical_id" | "parent_node_id" | "node_role" | "has_expectations" | "node_type"
    >
  >,
  options: {
    splitVisibilityReviewabilityEnabled: boolean;
  },
): CallNodeRoleSummary {
  const hasChildrenByNodeId = new Set(
    nodes
      .filter((node) => node.parent_node_id !== null)
      .map((node) => node.parent_node_id as string),
  );

  const byLogicalId = new Map<string, NodeRoleClassification>();
  const primarySubmittableNodeLogicalIds: string[] = [];
  const visibleSupportingNodeLogicalIds: string[] = [];
  const structuralContainerNodeLogicalIds: string[] = [];

  for (const node of nodes) {
    if (typeof node.logical_id !== "string" || node.logical_id.trim().length === 0) {
      continue;
    }
    const role = classifyNodeRole(node, {
      splitVisibilityReviewabilityEnabled: options.splitVisibilityReviewabilityEnabled,
      hasChildren: hasChildrenByNodeId.has(node.id),
    });
    byLogicalId.set(node.logical_id, role);

    if (role.isPrimarySubmittable) {
      primarySubmittableNodeLogicalIds.push(node.logical_id);
    }
    if (role.isSupporting && !role.isContainer) {
      visibleSupportingNodeLogicalIds.push(node.logical_id);
    }
    if (role.isContainer) {
      structuralContainerNodeLogicalIds.push(node.logical_id);
    }
  }

  return {
    byLogicalId,
    primarySubmittableNodeLogicalIds,
    visibleSupportingNodeLogicalIds,
    structuralContainerNodeLogicalIds,
  };
}
