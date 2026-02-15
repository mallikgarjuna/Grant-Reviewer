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
  return NextResponse.json(result.data, { status: 200 });
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
