import type { NodeSummary } from "@/lib/bff/types";

export type NodeMetadata = {
  title?: string | null;
};

export type RenderNode = {
  nodeLogicalId: string;
  label: string;
};

export type RenderModelReady = {
  state: "ready";
  nodes: RenderNode[];
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

type BuildRenderModelInput = {
  nodes: NodeSummary[];
  metadataByLogicalId: Record<string, NodeMetadata>;
};

function toFallbackLabel(logicalId: string): string {
  return logicalId
    .replace(/_/g, " ")
    .replace(/\b\w/g, (chunk) => chunk.toUpperCase());
}

export function buildRenderModel(input: BuildRenderModelInput): RenderModelResult {
  const nestedNodes = input.nodes.filter((node) => node.parent_node_id !== null);
  if (nestedNodes.length > 0) {
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

  return {
    state: "ready",
    nodes: input.nodes.map((node) => {
      const nodeLogicalId = node.logical_id as string;
      const metadata = input.metadataByLogicalId[nodeLogicalId];
      const label =
        (typeof metadata?.title === "string" && metadata.title.trim()) ||
        (typeof node.title === "string" && node.title.trim()) ||
        toFallbackLabel(nodeLogicalId);
      return {
        nodeLogicalId,
        label,
      };
    }),
  };
}
