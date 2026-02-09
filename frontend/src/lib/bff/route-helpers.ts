import { NextResponse } from "next/server";

import type { ApiError, BffRequestContext, Result } from "./types";

export function requireBffContext(externalUserId: string | null): Result<BffRequestContext> {
  if (!externalUserId) {
    return {
      ok: false,
      error: {
        code: "UNAUTHORIZED",
        message: "User is not authenticated.",
        details: {},
        status: 401,
      },
    };
  }
  return { ok: true, data: { externalUserId } };
}

export function apiErrorResponse(error: ApiError): NextResponse {
  return NextResponse.json(
    {
      error: {
        code: error.code,
        message: error.message,
        details: error.details ?? {},
      },
    },
    { status: error.status },
  );
}

