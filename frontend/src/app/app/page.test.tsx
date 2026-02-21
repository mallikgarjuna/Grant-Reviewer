import "@testing-library/jest-dom/vitest";

import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { act } from "react";
import { beforeEach, afterEach, describe, it, vi } from "vitest";

import AppSubmitPage from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

vi.mock("@/lib/review-attempt", () => ({
  MAX_SNIPPET_CHARS: 10_000,
  getStoredReviewAttempt: () => null,
  getOrCreateReviewAttempt: vi.fn(),
}));

type MockMode = "legacy" | "structured" | "fallback" | "not_found";

const CALLS_PAYLOAD = {
  calls: [
    {
      id: "call-legacy-id",
      code: "ERC-2026-COG",
      name: "ERC Consolidator Grant 2026",
      year: 2026,
      agency_short_name: "ERC",
    },
    {
      id: "call-structured-id",
      code: "nwo_veni_2025_preproposal",
      name: "NWO Talent Programme — Veni 2025 — Pre-proposal",
      year: 2025,
      agency_short_name: "NWO",
    },
  ],
};

const NODES_PAYLOAD = {
  nodes: [
    {
      id: "node-1",
      parent_node_id: null,
      title: "Section 1",
      node_type: "SECTION",
      order_index: 1,
      has_expectations: true,
    },
  ],
};

function jsonResponse(payload: unknown, status = 200): Response {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

function createFetchMock(mode: MockMode) {
  return vi.fn(async (input: string | URL | Request) => {
    const url = typeof input === "string" ? input : input instanceof URL ? input.toString() : input.url;

    if (url.includes("/api/bff/calls") && !url.includes("/nodes") && !url.includes("/config")) {
      return jsonResponse(CALLS_PAYLOAD);
    }

    if (url.includes("/api/bff/calls/ERC-2026-COG/config")) {
      return jsonResponse({
        call_logical_id: "ERC-2026-COG",
        config_version: "1",
        ui_mode: "legacy_single_snippet",
      });
    }

    if (url.includes("/api/bff/calls/nwo_veni_2025_preproposal/config")) {
      if (mode === "structured") {
        return jsonResponse({
          call_logical_id: "nwo_veni_2025_preproposal",
          config_version: "1",
          ui_mode: "structured_nodes",
          expected_nodes: ["academic_profile", "knowledge_utilisation", "scientific_proposal"],
        });
      }
      if (mode === "fallback") {
        return jsonResponse(
          {
            error: {
              code: "INTERNAL_ERROR",
              message: "Unable to load config",
              details: {},
            },
          },
          500,
        );
      }
      if (mode === "not_found") {
        return jsonResponse(
          {
            error: {
              code: "CALL_NOT_FOUND",
              message: "Funding call not found.",
              details: {},
            },
          },
          404,
        );
      }
      return jsonResponse({
        call_logical_id: "nwo_veni_2025_preproposal",
        config_version: "1",
        ui_mode: "legacy_single_snippet",
      });
    }

    if (url.includes("/api/bff/calls/call-legacy-id/nodes")) {
      return jsonResponse(NODES_PAYLOAD);
    }

    if (url.includes("/api/bff/calls/call-structured-id/nodes")) {
      return jsonResponse(NODES_PAYLOAD);
    }

    return jsonResponse(
      {
        error: {
          code: "INTERNAL_ERROR",
          message: `Unhandled URL in test mock: ${url}`,
          details: {},
        },
      },
      500,
    );
  });
}

async function selectCall(callId: string): Promise<void> {
  const select = await screen.findByLabelText("Funding Call");
  await act(async () => {
    fireEvent.change(select, { target: { value: callId } });
  });
}

describe("AppSubmitPage UI gating", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders legacy mode with active snippet and submit path", async () => {
    vi.stubGlobal("fetch", createFetchMock("legacy"));

    render(<AppSubmitPage />);
    await selectCall("call-legacy-id");

    const snippet = await screen.findByLabelText("Proposal Snippet");
    const submit = screen.getByRole("button", { name: "Generate Review" });

    await waitFor(() => {
      expect(snippet).toBeEnabled();
      expect(submit).toBeEnabled();
    });
  });

  it("renders structured disabled placeholder with no submit path", async () => {
    vi.stubGlobal("fetch", createFetchMock("structured"));

    render(<AppSubmitPage />);
    await selectCall("call-structured-id");

    expect(
      await screen.findByText(
        "Structured submissions are coming soon for this call. Please switch to a call using the legacy single-snippet mode for now.",
      ),
    ).toBeInTheDocument();

    const snippet = await screen.findByLabelText("Proposal Snippet");
    const submit = screen.getByRole("button", { name: "Generate Review" });
    expect(snippet).toBeDisabled();
    expect(submit).toBeDisabled();
  });

  it("renders fallback warning and keeps legacy path usable when config fetch fails", async () => {
    vi.stubGlobal("fetch", createFetchMock("fallback"));

    render(<AppSubmitPage />);
    await selectCall("call-structured-id");

    expect(
      await screen.findByText("Structured mode could not be loaded. Showing legacy mode instead."),
    ).toBeInTheDocument();

    const snippet = await screen.findByLabelText("Proposal Snippet");
    const submit = screen.getByRole("button", { name: "Generate Review" });
    expect(snippet).toBeEnabled();
    expect(submit).toBeEnabled();
  });

  it("renders call-not-found and disables submission controls on 404 config", async () => {
    vi.stubGlobal("fetch", createFetchMock("not_found"));

    render(<AppSubmitPage />);
    await selectCall("call-structured-id");

    expect(
      await screen.findByText(
        "The selected funding call configuration was not found. Submission is disabled for this call.",
      ),
    ).toBeInTheDocument();

    const snippet = await screen.findByLabelText("Proposal Snippet");
    const submit = screen.getByRole("button", { name: "Generate Review" });
    expect(snippet).toBeDisabled();
    expect(submit).toBeDisabled();
  });
});
