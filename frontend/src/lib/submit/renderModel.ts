// frontend/src/lib/submit/renderModel.ts
import type { NodeSummary } from "@/lib/bff/types";
import { classifyNodeRole } from "@/lib/submit/nodeRoles";

export type NodeMetadata = {
  title?: string | null;
  sourceSection?: string | null;
  parentLogicalId?: string | null;
  reviewStage?: "STEP_1" | "STEP_2" | "BOTH" | null;
};

export type RenderNode = {
  nodeLogicalId: string;
  label: string;
  reviewStage: "STEP_1" | "STEP_2" | "BOTH";
  nodeRole: "PRIMARY" | "SUPPORTING";
  isContainer: boolean;
};

export type RenderGroup = {
  groupKey: string;
  groupLabel: string | null;
  nodes: RenderNode[];
};

export type RenderModelReady = {
  state: "ready";
  nodes: RenderNode[];
  groups: RenderGroup[];
  metadataFallbackCount: number;
};

export type RenderModelUnsupported = {
  state: "unsupported";
  reason: "nested_nodes";
  message: string;
};

export type RenderModelContractError = {
  state: "contract_error";
  reason: "missing_logical_id";
  message: string;
  nodeIds: string[];
};

export type RenderModelResult =
  | RenderModelReady
  | RenderModelUnsupported
  | RenderModelContractError;

export type ReviewStage = "STEP_1" | "STEP_2";

type BuildRenderModelInput = {
  nodes: NodeSummary[];
  metadataByLogicalId: Record<string, NodeMetadata>;
  splitVisibilityReviewabilityEnabled?: boolean;
};

function toFallbackLabel(logicalId: string): string {
  return logicalId
    .replace(/_/g, " ")
    .replace(/\b\w/g, (chunk) => chunk.toUpperCase());
}

function normalizeSectionNumber(raw: string): string | null {
  const trimmed = raw.trim();
  if (!trimmed) {
    return null;
  }

  const compact = trimmed.replace(/\s+/g, "");
  const numericAlpha = compact.match(/^(\d+)([A-Za-z])$/);
  if (numericAlpha) {
    return `${numericAlpha[1]}.${numericAlpha[2].toLowerCase()}`;
  }

  const alreadyDotted = compact.match(/^(\d+)\.([A-Za-z])$/);
  if (alreadyDotted) {
    return `${alreadyDotted[1]}.${alreadyDotted[2].toLowerCase()}`;
  }

  const numericOnly = compact.match(/^\d+$/);
  if (numericOnly) {
    return compact;
  }

  const alphaNumericPart = compact.match(/^([A-Za-z]\d(?:\.[A-Za-z0-9]+)?)$/);
  if (alphaNumericPart) {
    return alphaNumericPart[1].toUpperCase();
  }

  const partMatch = trimmed.match(/Part\s+([A-Za-z]\d)/i);
  if (partMatch) {
    const subpartMatch = trimmed.match(/Part\s+(I{1,3}|IV|V)\b/i);
    if (subpartMatch) {
      return `${partMatch[1].toUpperCase()}.${subpartMatch[1].toUpperCase()}`;
    }
    return partMatch[1].toUpperCase();
  }

  return null;
}

export function buildRenderModel(input: BuildRenderModelInput): RenderModelResult {
  const splitVisibilityReviewabilityEnabled =
    input.splitVisibilityReviewabilityEnabled === true;
  const nestedNodes = input.nodes.filter((node) => node.parent_node_id !== null);
  const hasStructuralContainers = input.nodes.some((node) => !node.has_expectations);
  if (
    !splitVisibilityReviewabilityEnabled &&
    nestedNodes.length > 0 &&
    !hasStructuralContainers
  ) {
    return {
      state: "unsupported",
      reason: "nested_nodes",
      message: "This call uses nested sections and is not yet supported in this form.",
    };
  }

  const missingLogicalIdNodeIds = input.nodes
    .filter((node) => typeof node.logical_id !== "string" || node.logical_id.trim().length === 0)
    .map((node) => node.id);
  if (missingLogicalIdNodeIds.length > 0) {
    return {
      state: "contract_error",
      reason: "missing_logical_id",
      message: "This call cannot be rendered because one or more sections are missing logical ids.",
      nodeIds: missingLogicalIdNodeIds,
    };
  }

  const nodeById = new Map(input.nodes.map((node) => [node.id, node]));
  const renderNodeByLogicalId = new Map<string, RenderNode>();
  for (const node of input.nodes) {
    const nodeLogicalId = node.logical_id as string;
    const metadata = input.metadataByLogicalId[nodeLogicalId];
    const metadataTitle =
      typeof metadata?.title === "string" && metadata.title.trim() ? metadata.title : null;
    const nodeTitle = typeof node.title === "string" && node.title.trim() ? node.title : null;
    const sectionNumber =
      typeof metadata?.sourceSection === "string"
        ? normalizeSectionNumber(metadata.sourceSection)
        : null;
    const baseLabel = metadataTitle ?? nodeTitle ?? toFallbackLabel(nodeLogicalId);
    const reviewStage = metadata?.reviewStage ?? "BOTH";
    const role = classifyNodeRole(node, {
      splitVisibilityReviewabilityEnabled,
    });
    renderNodeByLogicalId.set(nodeLogicalId, {
      nodeLogicalId,
      label: sectionNumber ? `${baseLabel} (${sectionNumber})` : baseLabel,
      reviewStage,
      nodeRole: role.role,
      isContainer: role.isContainer,
    });
  }

  const visibleNodes = input.nodes.filter((node) => {
    const role = classifyNodeRole(node, {
      splitVisibilityReviewabilityEnabled,
    });
    if (splitVisibilityReviewabilityEnabled) {
      return !role.isContainer;
    }
    return node.has_expectations;
  });
  const groupsByKey = new Map<string, RenderGroup>();
  for (const leafNode of visibleNodes) {
    const leafLogicalId = leafNode.logical_id as string;
    const renderLeaf = renderNodeByLogicalId.get(leafLogicalId);
    if (!renderLeaf) {
      continue;
    }
    const ancestorLabels: string[] = [];
    let currentParentNodeId = leafNode.parent_node_id;
    while (currentParentNodeId) {
      const parentNode = nodeById.get(currentParentNodeId);
      if (!parentNode) {
        break;
      }
      if (parentNode.logical_id) {
        const metadata = input.metadataByLogicalId[parentNode.logical_id];
        const metadataTitle =
          typeof metadata?.title === "string" && metadata.title.trim()
            ? metadata.title
            : null;
        ancestorLabels.unshift(
          metadataTitle ??
            (parentNode.title.trim() ? parentNode.title : toFallbackLabel(parentNode.logical_id)),
        );
      }
      currentParentNodeId = parentNode.parent_node_id;
    }

    const parentLogicalId = input.metadataByLogicalId[leafLogicalId]?.parentLogicalId ?? null;
    const groupKey = ancestorLabels.join(" / ") || parentLogicalId || "__ungrouped__";
    const existingGroup = groupsByKey.get(groupKey);
    if (existingGroup) {
      existingGroup.nodes.push(renderLeaf);
      continue;
    }
    groupsByKey.set(groupKey, {
      groupKey,
      groupLabel: ancestorLabels.length > 0 ? ancestorLabels.join(" / ") : null,
      nodes: [renderLeaf],
    });
  }

  const readyNodes = visibleNodes
    .map((node) => {
      const nodeLogicalId = node.logical_id as string;
      return renderNodeByLogicalId.get(nodeLogicalId) ?? null;
    })
    .filter((node): node is RenderNode => node !== null);

  return {
    state: "ready",
    nodes: readyNodes,
    groups: Array.from(groupsByKey.values()),
    metadataFallbackCount: input.nodes.filter((node) => {
      const nodeLogicalId = node.logical_id as string;
      const metadata = input.metadataByLogicalId[nodeLogicalId];
      return !(typeof metadata?.title === "string" && metadata.title.trim());
    }).length,
  };
}

export function isNodeEligibleForStage(
  node: RenderNode,
  reviewStage: ReviewStage,
): boolean {
  if (node.reviewStage === "BOTH") {
    return true;
  }
  return node.reviewStage === reviewStage;
}
