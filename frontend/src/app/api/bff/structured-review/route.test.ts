// frontend/src/app/api/bff/structured-review/route.test.ts
// WF-0070 Task 3: BFF fail-closed validation for review_stage

import { beforeEach, describe, expect, it, vi } from "vitest";

// Mock server-only module
vi.mock("server-only", () => ({}));

// Mock Clerk
const authMock = vi.fn();
vi.mock("@clerk/nextjs/server", () => ({
  auth: authMock,
}));

// Mock server-env to return dummy values
vi.mock("@/lib/bff/server-env", () => ({
  getBffSharedSecret: () => "test-secret-key-32-chars-minimum-a",
  getFastApiBaseUrl: () => "http://localhost:8000",
}));

// Mock global fetch to capture outgoing requests
const fetchMock = vi.fn();
vi.stubGlobal("fetch", fetchMock);

function buildRequest(
  body: Record<string, unknown>,
  headers?: Record<string, string>,
): Request {
  return new Request("http://localhost/api/bff/structured-review", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Idempotency-Key": "test-idem-key",
      ...headers,
    },
    body: JSON.stringify(body),
  });
}

describe("POST /api/bff/structured-review", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.unstubAllEnvs();
    authMock.mockResolvedValue({ userId: "user-1" });
  });

  it("wf0070_t3_invalid_review_stage_returns_4xx_error", async () => {
    const { POST } = await import("./route");
    const response = await POST(
      buildRequest({
        review_stage: "INVALID",
        call_id: "00000000-0000-0000-0000-000000000001",
        nodes: [],
      }),
    );

    expect(response.status).toBeGreaterThanOrEqual(400);
    expect(response.status).toBeLessThan(500);

    const body = (await response.json()) as { error?: { code: string } };
    expect(body.error?.code).toBe("VALIDATION_ERROR");
  });

  it("wf0070_t3_missing_review_stage_returns_4xx_error", async () => {
    const { POST } = await import("./route");
    const response = await POST(
      buildRequest({
        call_id: "00000000-0000-0000-0000-000000000001",
        nodes: [],
      }),
    );

    expect(response.status).toBeGreaterThanOrEqual(400);
    expect(response.status).toBeLessThan(500);

    const body = (await response.json()) as { error?: { code: string } };
    expect(body.error?.code).toBe("VALIDATION_ERROR");
  });

  it("wf0070_t3_step_1_passes_through_unmodified", async () => {
    fetchMock.mockResolvedValue(
      new Response(JSON.stringify({ review_id: "r1", status: "COMPLETED" }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );

    const { POST } = await import("./route");
    const response = await POST(
      buildRequest({
        review_stage: "STEP_1",
        call_id: "00000000-0000-0000-0000-000000000001",
        nodes: [],
      }),
    );

    expect(response.status).toBe(200);
    // Verify the outgoing fetch was called with STEP_1 in body
    expect(fetchMock).toHaveBeenCalledTimes(1);
    const fetchBody = JSON.parse(fetchMock.mock.calls[0][1].body as string) as {
      review_stage: string;
    };
    expect(fetchBody.review_stage).toBe("STEP_1");
  });

  it("wf0070_t3_step_2_passes_through_unmodified", async () => {
    fetchMock.mockResolvedValue(
      new Response(JSON.stringify({ review_id: "r2", status: "COMPLETED" }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );

    const { POST } = await import("./route");
    const response = await POST(
      buildRequest({
        review_stage: "STEP_2",
        call_id: "00000000-0000-0000-0000-000000000001",
        nodes: [],
      }),
    );

    expect(response.status).toBe(200);
    expect(fetchMock).toHaveBeenCalledTimes(1);
    const fetchBody = JSON.parse(fetchMock.mock.calls[0][1].body as string) as {
      review_stage: string;
    };
    expect(fetchBody.review_stage).toBe("STEP_2");
  });
});
