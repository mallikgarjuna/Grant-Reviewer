import { auth } from "@clerk/nextjs/server";
import { NextResponse } from "next/server";

import { getCallConfig } from "@/lib/bff/adapter";
import { apiErrorResponse, requireBffContext } from "@/lib/bff/route-helpers";

type RouteContext = {
  params: Promise<{ callLogicalId: string }>;
};

export async function GET(_: Request, context: RouteContext) {
  const { userId } = await auth();
  const contextResult = requireBffContext(userId);
  if (!contextResult.ok) {
    return apiErrorResponse(contextResult.error);
  }

  const { callLogicalId } = await context.params;
  const result = await getCallConfig(contextResult.data, callLogicalId);
  if (!result.ok) {
    return apiErrorResponse(result.error);
  }

  return NextResponse.json(result.data, { status: 200 });
}
