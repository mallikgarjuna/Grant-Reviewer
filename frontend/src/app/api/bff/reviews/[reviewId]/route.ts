// frontend/src/app/api/bff/reviews/[reviewId]/route.ts
import { auth } from "@clerk/nextjs/server";
import { NextResponse } from "next/server";

import { deleteReview, getReview } from "@/lib/bff/adapter";
import { apiErrorResponse, requireBffContext } from "@/lib/bff/route-helpers";

type RouteContext = {
  params: Promise<{ reviewId: string }>;
};

function inferDetailState(record: Record<string, unknown>) {
  const callCode =
    typeof record.call_code === "string" ? record.call_code : null;
  const orderingSource =
    record.ordering_source === "review_payload_fallback"
      ? "review_payload_fallback"
      : "call_nodes";
  const unmappedNodeLogicalIds = Array.isArray(record.unmapped_node_logical_ids)
    ? record.unmapped_node_logical_ids.filter((item): item is string => typeof item === "string")
    : [];

  if (orderingSource === "review_payload_fallback" || record.call_id == null) {
    return "legacy_fallback";
  }
  if (callCode === "erc_stg_2026_full" && unmappedNodeLogicalIds.length > 0) {
    return "proof_path_unmapped";
  }
  return "call_linked";
}

function normalizeReviewDetailResponse(payload: unknown): unknown {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    return payload;
  }

  const record = payload as Record<string, unknown>;
  return {
    ...record,
    detail_state: inferDetailState(record),
    submitted_node_logical_ids: Array.isArray(record.submitted_node_logical_ids)
      ? record.submitted_node_logical_ids.filter((item): item is string => typeof item === "string")
      : [],
    unmapped_node_logical_ids: Array.isArray(record.unmapped_node_logical_ids)
      ? record.unmapped_node_logical_ids.filter((item): item is string => typeof item === "string")
      : [],
  };
}

export async function GET(_: Request, context: RouteContext) {
  const { userId } = await auth();
  const contextResult = requireBffContext(userId);
  if (!contextResult.ok) {
    return apiErrorResponse(contextResult.error);
  }

  const { reviewId } = await context.params;
  const result = await getReview(contextResult.data, reviewId);
  if (!result.ok) {
    return apiErrorResponse(result.error);
  }
  const payload = result.data as Record<string, unknown>;
  const submittedLeafIds = Array.isArray(payload.submitted_leaf_ids)
    ? payload.submitted_leaf_ids
    : [];
  const legacyAmbiguousContainerIds = Array.isArray(
    payload.legacy_ambiguous_container_ids,
  )
    ? payload.legacy_ambiguous_container_ids
    : [];
  const movedLegacyNodeReferences = Array.isArray(
    payload.moved_legacy_node_references,
  )
    ? payload.moved_legacy_node_references
    : [];
  return NextResponse.json(
    normalizeReviewDetailResponse({
      ...payload,
      submitted_leaf_ids: submittedLeafIds,
      legacy_ambiguous_container_ids: legacyAmbiguousContainerIds,
      moved_legacy_node_references: movedLegacyNodeReferences,
    }),
    { status: 200 },
  );
}

export async function DELETE(_: Request, context: RouteContext) {
  const { userId } = await auth();
  const contextResult = requireBffContext(userId);
  if (!contextResult.ok) {
    return apiErrorResponse(contextResult.error);
  }

  const { reviewId } = await context.params;
  const result = await deleteReview(contextResult.data, reviewId);
  if (!result.ok) {
    return apiErrorResponse(result.error);
  }
  return NextResponse.json(result.data, { status: 200 });
}
