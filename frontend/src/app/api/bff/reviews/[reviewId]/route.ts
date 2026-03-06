// frontend/src/app/api/bff/reviews/[reviewId]/route.ts
import { auth } from "@clerk/nextjs/server";
import { NextResponse } from "next/server";

import { deleteReview, getReview } from "@/lib/bff/adapter";
import { apiErrorResponse, requireBffContext } from "@/lib/bff/route-helpers";

type RouteContext = {
  params: Promise<{ reviewId: string }>;
};

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
    {
      ...payload,
      submitted_leaf_ids: submittedLeafIds,
      legacy_ambiguous_container_ids: legacyAmbiguousContainerIds,
      moved_legacy_node_references: movedLegacyNodeReferences,
    },
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
