import type { NodeSummary } from "@/lib/bff/types";

export type NodeMetadata = {
  title?: string | null;
  sourceSection?: string | null;
};

export type RenderNode = {
  nodeLogicalId: string;
  label: string;
};

export type RenderModelReady = {
  state: "ready";
  nodes: RenderNode[];
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

type BuildRenderModelInput = {
  nodes: NodeSummary[];
  metadataByLogicalId: Record<string, NodeMetadata>;
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
      const metadataTitle =
        typeof metadata?.title === "string" && metadata.title.trim()
          ? metadata.title
          : null;
      const nodeTitle =
        typeof node.title === "string" && node.title.trim() ? node.title : null;
      const sectionNumber =
        typeof metadata?.sourceSection === "string"
          ? normalizeSectionNumber(metadata.sourceSection)
          : null;
      const baseLabel = metadataTitle ?? nodeTitle ?? toFallbackLabel(nodeLogicalId);
      return {
        nodeLogicalId,
        label: sectionNumber ? `${baseLabel} (${sectionNumber})` : baseLabel,
      };
    }),
    metadataFallbackCount: input.nodes.filter((node) => {
      const nodeLogicalId = node.logical_id as string;
      const metadata = input.metadataByLogicalId[nodeLogicalId];
      return !(typeof metadata?.title === "string" && metadata.title.trim());
    }).length,
  };
}
