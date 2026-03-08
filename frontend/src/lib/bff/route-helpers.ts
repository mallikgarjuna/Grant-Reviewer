// frontend/src/lib/bff/route-helpers.ts
import { auth } from "@clerk/nextjs/server";
import { NextResponse } from "next/server";

import { resolveBypassUserId } from "@/lib/auth/testBypassAuth";

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

export async function resolveExternalUserId(request: Request): Promise<string | null> {
  const bypassUserId = await resolveBypassUserId(request);
  if (bypassUserId) {
    return bypassUserId;
  }
  const { userId } = await auth();
  return userId ?? null;
}
