import { auth } from "@clerk/nextjs/server";
import { NextResponse } from "next/server";

import { listNodes } from "@/lib/bff/adapter";
import { apiErrorResponse, requireBffContext } from "@/lib/bff/route-helpers";

type RouteContext = {
  params: Promise<{ callId: string }>;
};

export async function GET(_: Request, context: RouteContext) {
  const { userId } = await auth();
  const contextResult = requireBffContext(userId);
  if (!contextResult.ok) {
    return apiErrorResponse(contextResult.error);
  }

  const { callId } = await context.params;
  const result = await listNodes(contextResult.data, callId);
  if (!result.ok) {
    return apiErrorResponse(result.error);
  }
  return NextResponse.json(result.data, { status: 200 });
}

