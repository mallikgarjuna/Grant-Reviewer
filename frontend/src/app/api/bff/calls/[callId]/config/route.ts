import { NextResponse } from "next/server";

import { getCallConfig } from "@/lib/bff/adapter";
import {
  apiErrorResponse,
  requireBffContext,
  resolveExternalUserId,
} from "@/lib/bff/route-helpers";

type RouteContext = {
  params: Promise<{ callId: string }>;
};

export async function GET(request: Request, context: RouteContext) {
  const userId = await resolveExternalUserId(request);
  const contextResult = requireBffContext(userId);
  if (!contextResult.ok) {
    return apiErrorResponse(contextResult.error);
  }

  const { callId } = await context.params;
  const result = await getCallConfig(contextResult.data, callId);
  if (!result.ok) {
    return apiErrorResponse(result.error);
  }

  return NextResponse.json(result.data, { status: 200 });
}
