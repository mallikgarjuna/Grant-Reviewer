import { NextResponse } from "next/server";

import { listCalls } from "@/lib/bff/adapter";
import {
  apiErrorResponse,
  requireBffContext,
  resolveExternalUserId,
} from "@/lib/bff/route-helpers";

export async function GET(request: Request) {
  try {
    const userId = await resolveExternalUserId(request);
    const contextResult = requireBffContext(userId);
    if (!contextResult.ok) {
      return apiErrorResponse(contextResult.error);
    }

    const result = await listCalls(contextResult.data);
    if (!result.ok) {
      return apiErrorResponse(result.error);
    }
    return NextResponse.json(result.data, { status: 200 });
  } catch (error) {
    return apiErrorResponse({
      code: "INTERNAL_ERROR",
      message: "Failed to load calls.",
      details: {
        cause: error instanceof Error ? error.message : "unknown",
      },
      status: 500,
    });
  }
}
