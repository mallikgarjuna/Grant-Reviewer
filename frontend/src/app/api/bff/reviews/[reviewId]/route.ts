import { auth } from "@clerk/nextjs/server";
import { NextResponse } from "next/server";

import { deleteReview, getReview } from "@/lib/bff/adapter";
import { apiErrorResponse, requireBffContext } from "@/lib/bff/route-helpers";

type RouteContext = {
  params: Promise<{ reviewId: string }>;
};

function normalizeReviewDetailResponse(payload: unknown): unknown {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    return payload;
  }

  const record = payload as Record<string, unknown>;
  return {
    ...record,
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
  return NextResponse.json(normalizeReviewDetailResponse(result.data), { status: 200 });
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
