import "server-only";

import {
  buildSignaturePayload,
  normalizeSnippetText,
  sha256HexFromText,
  signSignaturePayload,
  stableJsonStringify,
} from "./crypto-utils.mjs";
import { getBffSharedSecret, getFastApiBaseUrl } from "./server-env";
import type {
    BffRequestContext,
    ComplianceCheckRequest,
    ComplianceCheckResponse,
    CallConfigResponse,
    CallsResponse,
  CreateReviewAttempt,
    CreateReviewRequest,
    CreateReviewResponse,
  DeleteReviewResponse,
    NodesResponse,
    Result,
    ReviewDetailResponse,
    StructuredReviewRequest,
    ReviewsListResponse,
} from "./types";

type BackendApiErrorShape = {
  error?: {
    code?: unknown;
    message?: unknown;
    details?: unknown;
  };
};

type FastApiRequestOptions = {
  path: string;
  method: "GET" | "POST" | "DELETE";
  context: BffRequestContext;
  bodyText?: string;
  idempotencyKey?: string;
};

function buildCanonicalCreateReviewPayload(
  payload: CreateReviewRequest,
): CreateReviewRequest {
  return {
    review_stage: payload.review_stage,
    call_id: payload.call_id,
    node_id: payload.node_id,
    snippet_text: normalizeSnippetText(payload.snippet_text),
  };
}

function parseApiError(
  responseStatus: number,
  parsedBody: unknown,
): { code: string; message: string; details: Record<string, unknown>; status: number } {
  if (
    parsedBody &&
    typeof parsedBody === "object" &&
    "error" in parsedBody
  ) {
    const candidate = parsedBody as BackendApiErrorShape;
    const code = candidate.error?.code;
    const message = candidate.error?.message;
    const details = candidate.error?.details;
    if (typeof code === "string" && typeof message === "string") {
      return {
        code,
        message,
        details:
          details && typeof details === "object" && !Array.isArray(details)
            ? (details as Record<string, unknown>)
            : {},
        status: responseStatus,
      };
    }
  }

  return {
    code: "INTERNAL_ERROR",
    message: "Unexpected API response shape.",
    details: {},
    status: responseStatus,
  };
}

function buildSignedHeaders(
  context: BffRequestContext,
  bodyText: string,
): Record<string, string> {
  const timestamp = Math.floor(Date.now() / 1000);
  const bodyBytes = new TextEncoder().encode(bodyText);
  const payload = buildSignaturePayload({
    userId: context.externalUserId,
    timestamp,
    bodyBytes,
  });
  const signature = signSignaturePayload(getBffSharedSecret(), payload);
  return {
    "X-GR-User-Id": context.externalUserId,
    "X-GR-Timestamp": String(timestamp),
    "X-GR-Signature": signature,
  };
}

async function requestFastApi<T>(
  options: FastApiRequestOptions,
): Promise<Result<T>> {
  const bodyText = options.bodyText ?? "";
  let signedHeaders: Record<string, string>;
  let fastApiBaseUrl: string;
  try {
    signedHeaders = buildSignedHeaders(options.context, bodyText);
    fastApiBaseUrl = getFastApiBaseUrl();
  } catch (error) {
    return {
      ok: false,
      error: {
        code: "INTERNAL_ERROR",
        message: "Backend gateway is not configured correctly.",
        details: {
          cause: error instanceof Error ? error.message : "unknown",
        },
        status: 500,
      },
    };
  }

  const headers: Record<string, string> = {
    Accept: "application/json",
    ...signedHeaders,
  };
  if (options.idempotencyKey) {
    headers["Idempotency-Key"] = options.idempotencyKey;
  }
  if (options.method === "POST") {
    headers["Content-Type"] = "application/json";
  }

  let response: Response;
  try {
    response = await fetch(`${fastApiBaseUrl}${options.path}`, {
      method: options.method,
      headers,
      body: options.method === "POST" ? bodyText : undefined,
      cache: "no-store",
    });
  } catch (error) {
    return {
      ok: false,
      error: {
        code: "INTERNAL_ERROR",
        message: "Unable to reach backend API.",
        details: {
          cause: error instanceof Error ? error.message : "unknown",
        },
        status: 500,
      },
    };
  }

  let parsedBody: unknown = null;
  const raw = await response.text();
  if (raw) {
    try {
      parsedBody = JSON.parse(raw);
    } catch {
      parsedBody = null;
    }
  }

  if (!response.ok) {
    return {
      ok: false,
      error: parseApiError(response.status, parsedBody),
    };
  }

  return { ok: true, data: parsedBody as T };
}

export type CreateReviewDraft = CreateReviewRequest;

export function normalizeCreateReviewDraft(
  payload: CreateReviewDraft,
): CreateReviewRequest {
  return buildCanonicalCreateReviewPayload(payload);
}

export function buildCreateReviewPayloadSha256(
  payload: CreateReviewDraft,
): string {
  const normalized = normalizeCreateReviewDraft(payload);
  return sha256HexFromText(stableJsonStringify(normalized));
}

export async function listCalls(
  context: BffRequestContext,
): Promise<Result<CallsResponse>> {
  return requestFastApi<CallsResponse>({
    path: "/calls",
    method: "GET",
    context,
  });
}

export async function listNodes(
  context: BffRequestContext,
  callId: string,
): Promise<Result<NodesResponse>> {
  return requestFastApi<NodesResponse>({
    path: `/calls/${callId}/nodes`,
    method: "GET",
    context,
  });
}

export async function getCallConfig(
  context: BffRequestContext,
  callLogicalId: string,
): Promise<Result<CallConfigResponse>> {
  return requestFastApi<CallConfigResponse>({
    path: `/api/public/calls/${callLogicalId}/config`,
    method: "GET",
    context,
  });
}

export async function createReview(
  context: BffRequestContext,
  payload: CreateReviewRequest,
  attempt: CreateReviewAttempt,
): Promise<Result<CreateReviewResponse>> {
  const normalizedPayload = buildCanonicalCreateReviewPayload(payload);
  const bodyText = JSON.stringify(normalizedPayload);
  return requestFastApi<CreateReviewResponse>({
    path: "/reviews",
    method: "POST",
    context,
    bodyText,
    idempotencyKey: attempt.idempotencyKey,
  });
}

export async function checkCompliance(
  context: BffRequestContext,
  payload: ComplianceCheckRequest,
): Promise<Result<ComplianceCheckResponse>> {
  const bodyText = JSON.stringify(payload);
  return requestFastApi<ComplianceCheckResponse>({
    path: "/api/check-compliance",
    method: "POST",
    context,
    bodyText,
  });
}

export async function createStructuredReview(
  context: BffRequestContext,
  payload: StructuredReviewRequest,
  attempt: Pick<CreateReviewAttempt, "idempotencyKey">,
): Promise<Result<CreateReviewResponse>> {
  const bodyText = JSON.stringify(payload);
  return requestFastApi<CreateReviewResponse>({
    path: "/api/structured-review",
    method: "POST",
    context,
    bodyText,
    idempotencyKey: attempt.idempotencyKey,
  });
}

export async function getReview(
  context: BffRequestContext,
  reviewId: string,
): Promise<Result<ReviewDetailResponse>> {
  return requestFastApi<ReviewDetailResponse>({
    path: `/reviews/${reviewId}`,
    method: "GET",
    context,
  });
}

export async function deleteReview(
  context: BffRequestContext,
  reviewId: string,
): Promise<Result<DeleteReviewResponse>> {
  return requestFastApi<DeleteReviewResponse>({
    path: `/reviews/${reviewId}`,
    method: "DELETE",
    context,
  });
}

export async function listReviews(
  context: BffRequestContext,
): Promise<Result<ReviewsListResponse>> {
  return requestFastApi<ReviewsListResponse>({
    path: "/reviews",
    method: "GET",
    context,
  });
}
