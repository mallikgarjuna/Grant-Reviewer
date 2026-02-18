import type { NodeSummary } from "@/lib/bff/types";

export const OTHER_SECTIONS_PARENT_KEY = "__OTHER_SECTIONS__";
export const OTHER_SECTIONS_PARENT_LABEL = "Other Sections";

export type NodeParentOption = {
  id: string;
  label: string;
};

export type NodeChildOption = {
  id: string;
  label: string;
};

export type NodeHierarchyOptions = {
  parentOptions: NodeParentOption[];
  childrenByParent: Record<string, NodeChildOption[]>;
  parentByNodeId: Record<string, string>;
};

function compareNodes(a: NodeSummary, b: NodeSummary): number {
  if (a.order_index !== b.order_index) {
    return a.order_index - b.order_index;
  }
  return a.title.localeCompare(b.title);
}

export function buildNodeHierarchyOptions(nodes: NodeSummary[]): NodeHierarchyOptions {
  const nodeById = new Map(nodes.map((node) => [node.id, node]));
  const parentByNodeId: Record<string, string> = {};
  const childrenByParentNodes = new Map<string, NodeSummary[]>();
  const parentLabels = new Map<string, string>();

  for (const node of nodes) {
    const parentNode = node.parent_node_id ? nodeById.get(node.parent_node_id) : undefined;
    const parentId = parentNode?.id ?? OTHER_SECTIONS_PARENT_KEY;
    const parentLabel = parentNode?.title ?? OTHER_SECTIONS_PARENT_LABEL;
    parentByNodeId[node.id] = parentId;
    parentLabels.set(parentId, parentLabel);
    const bucket = childrenByParentNodes.get(parentId) ?? [];
    bucket.push(node);
    childrenByParentNodes.set(parentId, bucket);
  }

  const duplicatedTitleCounts = new Map<string, number>();
  for (const node of nodes) {
    duplicatedTitleCounts.set(node.title, (duplicatedTitleCounts.get(node.title) ?? 0) + 1);
  }

  const parentOptions = Array.from(parentLabels.entries())
    .map(([id, label]) => ({ id, label }))
    .sort((a, b) => {
      if (a.id === OTHER_SECTIONS_PARENT_KEY) {
        return 1;
      }
      if (b.id === OTHER_SECTIONS_PARENT_KEY) {
        return -1;
      }
      return a.label.localeCompare(b.label);
    });

  const childrenByParent: Record<string, NodeChildOption[]> = {};
  for (const parentOption of parentOptions) {
    const parentNodes = [...(childrenByParentNodes.get(parentOption.id) ?? [])].sort(compareNodes);
    childrenByParent[parentOption.id] = parentNodes.map((node) => {
      const isAmbiguous = (duplicatedTitleCounts.get(node.title) ?? 0) > 1;
      return {
        id: node.id,
        label: isAmbiguous ? `${node.title} (${parentOption.label})` : node.title,
      };
    });
  }

  return { parentOptions, childrenByParent, parentByNodeId };
}
