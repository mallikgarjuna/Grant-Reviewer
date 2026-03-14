import { NextResponse } from "next/server";

import { buildSignaturePayload, signSignaturePayload } from "@/lib/bff/crypto-utils.mjs";
import {
  apiErrorResponse,
  requireBffContext,
  resolveExternalUserId,
} from "@/lib/bff/route-helpers";
import { getBffSharedSecret, getFastApiBaseUrl } from "@/lib/bff/server-env";

export const runtime = "nodejs";
export const maxDuration = 60;
const WF0080_SUPPORT_TRACE_HEADER = "X-GR-Support-Trace";

function buildSignedHeaders(externalUserId: string, bodyText: string): Record<string, string> {
  const timestamp = Math.floor(Date.now() / 1000);
  const bodyBytes = new TextEncoder().encode(bodyText);
  const payload = buildSignaturePayload({
    userId: externalUserId,
    timestamp,
    bodyBytes,
  });
  const signature = signSignaturePayload(getBffSharedSecret(), payload);

  return {
    Accept: "application/json",
    "Content-Type": "application/json",
    "X-GR-User-Id": externalUserId,
    "X-GR-Timestamp": String(timestamp),
    "X-GR-Signature": signature,
  };
}

export async function POST(request: Request) {
  const userId = await resolveExternalUserId(request);
  const contextResult = requireBffContext(userId);
  if (!contextResult.ok) {
    return apiErrorResponse(contextResult.error);
  }

  const idempotencyKey = request.headers.get("Idempotency-Key")?.trim() ?? "";
  if (!idempotencyKey) {
    return apiErrorResponse({
      code: "VALIDATION_ERROR",
      message: "Missing required Idempotency-Key header.",
      details: {},
      status: 400,
    });
  }

  let bodyText = "{}";
  try {
    const parsed = (await request.json()) as Record<string, unknown>;

    // WF-0070 Task 3: fail-closed — reject invalid or missing review_stage.
    const reviewStage = parsed.review_stage;
    if (reviewStage !== "STEP_1" && reviewStage !== "STEP_2") {
      return apiErrorResponse({
        code: "VALIDATION_ERROR",
        message: "Invalid or missing review_stage. Must be STEP_1 or STEP_2.",
        details: { received: reviewStage ?? null },
        status: 400,
      });
    }

    bodyText = JSON.stringify({
      ...parsed,
      review_stage: reviewStage,
    });
  } catch {
    return apiErrorResponse({
      code: "VALIDATION_ERROR",
      message: "Invalid request payload.",
      details: {},
      status: 400,
    });
  }

  try {
    const response = await fetch(`${getFastApiBaseUrl()}/api/structured-review`, {
      method: "POST",
      headers: {
        ...buildSignedHeaders(contextResult.data.externalUserId, bodyText),
        "Idempotency-Key": idempotencyKey,
      },
      body: bodyText,
      cache: "no-store",
    });

    const raw = await response.text();
    const supportTraceHeader = response.headers.get(WF0080_SUPPORT_TRACE_HEADER);
    const responseHeaders = supportTraceHeader
      ? { [WF0080_SUPPORT_TRACE_HEADER]: supportTraceHeader }
      : undefined;
    if (!raw) {
      return new NextResponse(null, {
        status: response.status,
        headers: responseHeaders,
      });
    }

    try {
      const parsed = JSON.parse(raw) as unknown;
      return NextResponse.json(parsed, {
        status: response.status,
        headers: responseHeaders,
      });
    } catch {
      return new NextResponse(raw, {
        status: response.status,
        headers: {
          "Content-Type": "application/json",
          ...(responseHeaders ?? {}),
        },
      });
    }
  } catch (error) {
    return apiErrorResponse({
      code: "INTERNAL_ERROR",
      message: "Unable to reach backend API.",
      details: {
        cause: error instanceof Error ? error.message : "unknown",
      },
      status: 500,
    });
  }
}
