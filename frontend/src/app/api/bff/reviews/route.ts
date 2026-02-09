import { auth } from "@clerk/nextjs/server";
import { NextResponse } from "next/server";

import {
  buildCreateReviewPayloadSha256,
  createReview,
  normalizeCreateReviewDraft,
} from "@/lib/bff/adapter";
import { apiErrorResponse, requireBffContext } from "@/lib/bff/route-helpers";

type CreateReviewBody = {
  call_id?: unknown;
  node_id?: unknown;
  snippet_text?: unknown;
  idempotency_key?: unknown;
  payload_sha256?: unknown;
  created_at_ms?: unknown;
};

function validationError(message: string) {
  return apiErrorResponse({
    code: "VALIDATION_ERROR",
    message,
    details: {},
    status: 400,
  });
}

export async function POST(request: Request) {
  const { userId } = await auth();
  const contextResult = requireBffContext(userId);
  if (!contextResult.ok) {
    return apiErrorResponse(contextResult.error);
  }

  const body = (await request.json()) as CreateReviewBody;
  if (
    typeof body.call_id !== "string" ||
    typeof body.node_id !== "string" ||
    typeof body.snippet_text !== "string" ||
    typeof body.idempotency_key !== "string" ||
    typeof body.payload_sha256 !== "string" ||
    typeof body.created_at_ms !== "number"
  ) {
    return validationError("Invalid review request payload.");
  }

  const payload = normalizeCreateReviewDraft({
    call_id: body.call_id,
    node_id: body.node_id,
    snippet_text: body.snippet_text,
  });

  const derivedPayloadSha256 = buildCreateReviewPayloadSha256(payload);
  if (derivedPayloadSha256 !== body.payload_sha256) {
    return validationError("Payload hash mismatch for current draft.");
  }

  const result = await createReview(contextResult.data, payload, {
    idempotencyKey: body.idempotency_key,
    payloadSha256: body.payload_sha256,
    createdAtMs: body.created_at_ms,
  });

  if (!result.ok) {
    return apiErrorResponse(result.error);
  }
  return NextResponse.json(result.data, { status: 200 });
}

