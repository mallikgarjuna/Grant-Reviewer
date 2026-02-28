import { describe, expect, it, vi } from "vitest";

import type { CallSummary } from "@/lib/bff/types";
import {
  loadStructuredCalls,
  type StructuredCallsWarning,
} from "@/lib/submit/loadStructuredCalls";

const CALLS: CallSummary[] = [
  {
    id: "call-1",
    code: "call_1",
    name: "Call 1",
    year: 2025,
    agency_short_name: "NWO",
  },
  {
    id: "call-2",
    code: "call_2",
    name: "Call 2",
    year: 2025,
    agency_short_name: "NWO",
  },
];

describe("loadStructuredCalls", () => {
  it("filters to structured_nodes calls", async () => {
    const fetchImpl = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith("/call_1/config")) {
        return new Response(
          JSON.stringify({
            call_logical_id: "call_1",
            config_version: "1",
            ui_mode: "structured_nodes",
            expected_nodes: [],
          }),
          { status: 200 },
        );
      }
      return new Response(
        JSON.stringify({
          call_logical_id: "call_2",
          config_version: "1",
          ui_mode: "legacy_single_snippet",
          expected_nodes: [],
        }),
        { status: 200 },
      );
    });

    const result = await loadStructuredCalls({
      calls: CALLS,
      fetchImpl,
    });

    expect(result.calls.map((call) => call.id)).toEqual(["call-1"]);
    expect(result.warnings).toHaveLength(0);
  });

  it("marks timeout warning and excludes timed out config", async () => {
    vi.useFakeTimers();
    const fetchImpl = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith("/call_1/config")) {
        return new Promise<Response>(() => {});
      }
      return new Response(
        JSON.stringify({
          call_logical_id: "call_2",
          config_version: "1",
          ui_mode: "structured_nodes",
          expected_nodes: [],
        }),
        { status: 200 },
      );
    });

    const pending = loadStructuredCalls({
      calls: CALLS,
      fetchImpl,
      timeoutMs: 100,
    });
    await vi.advanceTimersByTimeAsync(200);
    const result = await pending;
    vi.useRealTimers();

    expect(result.calls.map((call) => call.id)).toEqual(["call-2"]);
    expect(result.warnings).toContainEqual(
      expect.objectContaining<StructuredCallsWarning>({
        callCode: "call_1",
        reason: "timeout",
      }),
    );
  });

  it("aggregates partial failures while keeping eligible calls", async () => {
    const fetchImpl = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith("/call_1/config")) {
        return new Response(
          JSON.stringify({
            call_logical_id: "call_1",
            config_version: "1",
            ui_mode: "structured_nodes",
            expected_nodes: [],
          }),
          { status: 200 },
        );
      }
      return new Response(
        JSON.stringify({
          error: {
            code: "INTERNAL_ERROR",
            message: "boom",
          },
        }),
        { status: 500 },
      );
    });

    const result = await loadStructuredCalls({
      calls: CALLS,
      fetchImpl,
    });

    expect(result.calls.map((call) => call.id)).toEqual(["call-1"]);
    expect(result.warnings).toContainEqual(
      expect.objectContaining<StructuredCallsWarning>({
        callCode: "call_2",
        reason: "http_error",
      }),
    );
  });

  it("encodes call code when requesting config endpoint", async () => {
    const calls: CallSummary[] = [
      {
        id: "call-encoded",
        code: "call/with space",
        name: "Encoded",
        year: 2025,
        agency_short_name: "NWO",
      },
    ];
    const fetchImpl = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      expect(url).toBe("/api/bff/calls/call%2Fwith%20space/config");
      return new Response(
        JSON.stringify({
          call_logical_id: "call/with space",
          config_version: "1",
          ui_mode: "structured_nodes",
          expected_nodes: [],
        }),
        { status: 200 },
      );
    });

    const result = await loadStructuredCalls({ calls, fetchImpl });
    expect(result.calls.map((call) => call.id)).toEqual(["call-encoded"]);
  });
});
