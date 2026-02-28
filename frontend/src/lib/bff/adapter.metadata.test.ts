import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("server-only", () => ({}));

describe("adapter getCallNodeMetadata", () => {
  const originalEnv = { ...process.env };

  beforeEach(() => {
    vi.restoreAllMocks();
    process.env = {
      ...originalEnv,
      FASTAPI_BASE_URL: "http://backend.test",
      BFF_SHARED_SECRET: "shared-secret",
    };
  });

  it("uses metadata endpoint path and parses payload", async () => {
    const fetchMock = vi.fn(async () => {
      return new Response(
        JSON.stringify({
          call_logical_id: "nwo_veni_2025_preproposal",
          nodes: [
            {
              logical_id: "academic_profile",
              title: "Academic Profile",
              word_limit_min: 0,
              word_limit_max: 500,
            },
          ],
          unknown_node_logical_ids: null,
        }),
        { status: 200 },
      );
    });
    vi.stubGlobal("fetch", fetchMock);
    const { getCallNodeMetadata } = await import("@/lib/bff/adapter");

    const result = await getCallNodeMetadata(
      { externalUserId: "user-1" },
      "nwo_veni_2025_preproposal",
    );

    expect(result.ok).toBe(true);
    if (!result.ok) {
      return;
    }
    expect(result.data.call_logical_id).toBe("nwo_veni_2025_preproposal");
    expect(result.data.nodes[0]?.logical_id).toBe("academic_profile");

    expect(fetchMock).toHaveBeenCalledWith(
      "http://backend.test/api/public/calls/nwo_veni_2025_preproposal/nodes/metadata",
      expect.objectContaining({
        method: "GET",
      }),
    );
  });
});
