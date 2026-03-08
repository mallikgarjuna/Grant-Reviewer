import { beforeEach, describe, expect, it, vi } from "vitest";
import { buildTestBypassToken } from "@/lib/auth/testBypassAuth";

vi.mock("server-only", () => ({}));

const authMock = vi.fn();
const getCallNodeMetadataMock = vi.fn();

vi.mock("@clerk/nextjs/server", () => ({
  auth: authMock,
}));

vi.mock("@/lib/bff/adapter", () => ({
  getCallNodeMetadata: getCallNodeMetadataMock,
}));

describe("GET /api/bff/calls/[callId]/metadata", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.unstubAllEnvs();
  });

  it("returns metadata payload when auth and adapter succeed", async () => {
    authMock.mockResolvedValue({ userId: "user-1" });
    getCallNodeMetadataMock.mockResolvedValue({
      ok: true,
      data: {
        call_logical_id: "nwo_veni_2025_preproposal",
        nodes: [],
        unknown_node_logical_ids: null,
      },
    });

    const { GET } = await import("./route");
    const response = await GET(new Request("http://localhost"), {
      params: Promise.resolve({ callId: "nwo_veni_2025_preproposal" }),
    });
    const body = (await response.json()) as { call_logical_id: string };

    expect(response.status).toBe(200);
    expect(body.call_logical_id).toBe("nwo_veni_2025_preproposal");
    expect(getCallNodeMetadataMock).toHaveBeenCalledWith(
      { externalUserId: "user-1" },
      "nwo_veni_2025_preproposal",
    );
  });

  it("maps adapter errors through apiErrorResponse", async () => {
    authMock.mockResolvedValue({ userId: "user-1" });
    getCallNodeMetadataMock.mockResolvedValue({
      ok: false,
      error: {
        code: "NOT_FOUND",
        message: "Call not found",
        details: {},
        status: 404,
      },
    });

    const { GET } = await import("./route");
    const response = await GET(new Request("http://localhost"), {
      params: Promise.resolve({ callId: "missing_call" }),
    });
    const body = (await response.json()) as { error: { code: string } };

    expect(response.status).toBe(404);
    expect(body.error.code).toBe("NOT_FOUND");
  });

  it("accepts test bypass auth when AUTH_MODE=test_bypass", async () => {
    vi.stubEnv("AUTH_MODE", "test_bypass");
    vi.stubEnv("NODE_ENV", "test");
    vi.stubEnv("TEST_AUTH_SECRET", "dev-secret");
    const token = await buildTestBypassToken("bypass_user");

    getCallNodeMetadataMock.mockResolvedValue({
      ok: true,
      data: {
        call_logical_id: "nwo_veni_2025_preproposal",
        nodes: [],
        unknown_node_logical_ids: null,
      },
    });

    const { GET } = await import("./route");
    const response = await GET(
      new Request("http://localhost", {
        headers: {
          cookie: `gr_test_auth=${encodeURIComponent(token)}`,
        },
      }),
      {
        params: Promise.resolve({ callId: "nwo_veni_2025_preproposal" }),
      },
    );
    const body = (await response.json()) as { call_logical_id: string };

    expect(response.status).toBe(200);
    expect(body.call_logical_id).toBe("nwo_veni_2025_preproposal");
    expect(getCallNodeMetadataMock).toHaveBeenCalledWith(
      { externalUserId: "bypass_user" },
      "nwo_veni_2025_preproposal",
    );
    expect(authMock).not.toHaveBeenCalled();
  });
});
