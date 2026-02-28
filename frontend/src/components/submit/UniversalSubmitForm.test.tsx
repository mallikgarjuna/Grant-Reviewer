import "@testing-library/jest-dom/vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { UniversalSubmitForm } from "@/components/submit/UniversalSubmitForm";

const push = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push }),
}));

describe("UniversalSubmitForm", () => {
  const originalCrypto = globalThis.crypto;

  beforeEach(() => {
    vi.restoreAllMocks();
    push.mockReset();
    window.localStorage.clear();
    Object.defineProperty(globalThis, "crypto", {
      value: {
        ...originalCrypto,
        randomUUID: () => "fixed-idempotency-key",
      },
      configurable: true,
    });
    vi.spyOn(console, "info").mockImplementation(() => {});
  });

  it("renders dynamic node fields from API order", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url === "/api/bff/calls") {
        return new Response(
          JSON.stringify({
            calls: [
              {
                id: "call-1",
                code: "nwo_veni_2025_preproposal",
                name: "NWO Veni",
                year: 2025,
                agency_short_name: "NWO",
              },
            ],
          }),
          { status: 200 },
        );
      }
      if (url === "/api/bff/calls/call-1/nodes") {
        return new Response(
          JSON.stringify({
            nodes: [
              {
                id: "node-2",
                logical_id: "research_idea",
                title: "Research Idea",
                parent_node_id: null,
                node_type: "SECTION",
                order_index: 2,
                has_expectations: true,
              },
              {
                id: "node-1",
                logical_id: "academic_profile",
                title: "Academic Profile",
                parent_node_id: null,
                node_type: "SECTION",
                order_index: 1,
                has_expectations: true,
              },
            ],
          }),
          { status: 200 },
        );
      }
      if (url === "/api/bff/calls/nwo_veni_2025_preproposal/config") {
        return new Response(
          JSON.stringify({
            call_logical_id: "nwo_veni_2025_preproposal",
            config_version: "1",
            ui_mode: "structured_nodes",
            expected_nodes: [],
          }),
          { status: 200 },
        );
      }
      if (url === "/api/bff/calls/nwo_veni_2025_preproposal/metadata") {
        return new Response(
          JSON.stringify({
            call_logical_id: "nwo_veni_2025_preproposal",
            nodes: [],
            unknown_node_logical_ids: null,
          }),
          { status: 200 },
        );
      }
      return new Response(JSON.stringify({ is_compliant: true, errors: [], warnings: [] }), {
        status: 200,
      });
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<UniversalSubmitForm />);

    const fields = await screen.findAllByRole("textbox");
    expect(fields).toHaveLength(2);
    expect(fields[0]).toHaveAccessibleName("Research Idea");
    expect(fields[1]).toHaveAccessibleName("Academic Profile");
  });

  it("blocks submit when all dynamic nodes are empty", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url === "/api/bff/calls") {
        return new Response(
          JSON.stringify({
            calls: [
              {
                id: "call-1",
                code: "nwo_veni_2025_preproposal",
                name: "NWO Veni",
                year: 2025,
                agency_short_name: "NWO",
              },
            ],
          }),
          { status: 200 },
        );
      }
      if (url === "/api/bff/calls/call-1/nodes") {
        return new Response(
          JSON.stringify({
            nodes: [
              {
                id: "node-1",
                logical_id: "academic_profile",
                title: "Academic Profile",
                parent_node_id: null,
                node_type: "SECTION",
                order_index: 1,
                has_expectations: true,
              },
            ],
          }),
          { status: 200 },
        );
      }
      if (url === "/api/bff/calls/nwo_veni_2025_preproposal/config") {
        return new Response(
          JSON.stringify({
            call_logical_id: "nwo_veni_2025_preproposal",
            config_version: "1",
            ui_mode: "structured_nodes",
            expected_nodes: [],
          }),
          { status: 200 },
        );
      }
      if (url === "/api/bff/calls/nwo_veni_2025_preproposal/metadata") {
        return new Response(
          JSON.stringify({
            call_logical_id: "nwo_veni_2025_preproposal",
            nodes: [],
            unknown_node_logical_ids: null,
          }),
          { status: 200 },
        );
      }
      return new Response(JSON.stringify({ ok: true }), { status: 200 });
    });
    vi.stubGlobal("fetch", fetchMock);
    render(<UniversalSubmitForm />);

    fireEvent.click(await screen.findByRole("button", { name: "Submit" }));
    expect(
      await screen.findByText("You must fill out at least one section before submitting."),
    ).toBeInTheDocument();
    expect(fetchMock).not.toHaveBeenCalledWith(
      "/api/bff/structured-review",
      expect.anything(),
    );
  });

  it("sends Idempotency-Key header during submit", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url === "/api/bff/calls") {
        return new Response(
          JSON.stringify({
            calls: [
              {
                id: "call-1",
                code: "nwo_veni_2025_preproposal",
                name: "NWO Veni",
                year: 2025,
                agency_short_name: "NWO",
              },
            ],
          }),
          { status: 200 },
        );
      }
      if (url === "/api/bff/calls/call-1/nodes") {
        return new Response(
          JSON.stringify({
            nodes: [
              {
                id: "node-1",
                logical_id: "academic_profile",
                title: "Academic Profile",
                parent_node_id: null,
                node_type: "SECTION",
                order_index: 1,
                has_expectations: true,
              },
            ],
          }),
          { status: 200 },
        );
      }
      if (url === "/api/bff/calls/nwo_veni_2025_preproposal/config") {
        return new Response(
          JSON.stringify({
            call_logical_id: "nwo_veni_2025_preproposal",
            config_version: "1",
            ui_mode: "structured_nodes",
            expected_nodes: [],
          }),
          { status: 200 },
        );
      }
      if (url === "/api/bff/calls/nwo_veni_2025_preproposal/metadata") {
        return new Response(
          JSON.stringify({
            call_logical_id: "nwo_veni_2025_preproposal",
            nodes: [],
            unknown_node_logical_ids: null,
          }),
          { status: 200 },
        );
      }
      if (url === "/api/bff/check-compliance") {
        return new Response(JSON.stringify({ is_compliant: true, errors: [], warnings: [] }), {
          status: 200,
        });
      }
      if (url === "/api/bff/structured-review") {
        expect(init?.headers).toMatchObject({
          "Content-Type": "application/json",
          "Idempotency-Key": "fixed-idempotency-key",
        });
        return new Response(JSON.stringify({ review_id: "review-1" }), { status: 200 });
      }
      return new Response(JSON.stringify({ error: { code: "NOT_FOUND", message: "not found" } }), {
        status: 404,
      });
    });
    vi.stubGlobal("fetch", fetchMock);
    render(<UniversalSubmitForm />);

    fireEvent.change(await screen.findByLabelText("Academic Profile"), {
      target: { value: "filled" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Submit" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/bff/structured-review",
        expect.objectContaining({ method: "POST" }),
      ),
    );
  });

  it("shows gating warning for partial config failures", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url === "/api/bff/calls") {
        return new Response(
          JSON.stringify({
            calls: [
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
            ],
          }),
          { status: 200 },
        );
      }
      if (url === "/api/bff/calls/call_1/config") {
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
      if (url === "/api/bff/calls/call_2/config") {
        return new Response(
          JSON.stringify({ error: { code: "INTERNAL_ERROR", message: "boom" } }),
          { status: 500 },
        );
      }
      if (url === "/api/bff/calls/call-1/nodes") {
        return new Response(
          JSON.stringify({
            nodes: [
              {
                id: "node-1",
                logical_id: "academic_profile",
                title: "Academic Profile",
                parent_node_id: null,
                node_type: "SECTION",
                order_index: 1,
                has_expectations: true,
              },
            ],
          }),
          { status: 200 },
        );
      }
      return new Response(JSON.stringify({ is_compliant: true, errors: [], warnings: [] }), {
        status: 200,
      });
    });
    vi.stubGlobal("fetch", fetchMock);
    render(<UniversalSubmitForm />);

    expect(await screen.findByText("Some calls were hidden due to config loading issues.")).toBeInTheDocument();
    expect(screen.getByRole("combobox")).toHaveTextContent("call_1 - Call 1");
    expect(screen.getByRole("combobox")).not.toHaveTextContent("call_2 - Call 2");
  });

  it("shows unsupported state for nested node calls", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url === "/api/bff/calls") {
        return new Response(
          JSON.stringify({
            calls: [
              {
                id: "call-1",
                code: "call_1",
                name: "Call 1",
                year: 2025,
                agency_short_name: "NWO",
              },
            ],
          }),
          { status: 200 },
        );
      }
      if (url === "/api/bff/calls/call_1/config") {
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
      if (url === "/api/bff/calls/call-1/nodes") {
        return new Response(
          JSON.stringify({
            nodes: [
              {
                id: "node-1",
                logical_id: "root",
                title: "Root",
                parent_node_id: null,
                node_type: "SECTION",
                order_index: 1,
                has_expectations: true,
              },
              {
                id: "node-2",
                logical_id: "child",
                title: "Child",
                parent_node_id: "node-1",
                node_type: "SUBSECTION",
                order_index: 2,
                has_expectations: true,
              },
            ],
          }),
          { status: 200 },
        );
      }
      return new Response(JSON.stringify({ ok: true }), { status: 200 });
    });
    vi.stubGlobal("fetch", fetchMock);
    render(<UniversalSubmitForm />);

    expect(
      await screen.findByText("This call uses nested sections and is not yet supported in this form."),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Submit" })).toBeDisabled();
  });

  it("shows contract error for missing logical_id", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url === "/api/bff/calls") {
        return new Response(
          JSON.stringify({
            calls: [
              {
                id: "call-1",
                code: "call_1",
                name: "Call 1",
                year: 2025,
                agency_short_name: "NWO",
              },
            ],
          }),
          { status: 200 },
        );
      }
      if (url === "/api/bff/calls/call_1/config") {
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
      if (url === "/api/bff/calls/call-1/nodes") {
        return new Response(
          JSON.stringify({
            nodes: [
              {
                id: "node-1",
                logical_id: null,
                title: "Broken node",
                parent_node_id: null,
                node_type: "SECTION",
                order_index: 1,
                has_expectations: true,
              },
            ],
          }),
          { status: 200 },
        );
      }
      return new Response(JSON.stringify({ ok: true }), { status: 200 });
    });
    vi.stubGlobal("fetch", fetchMock);
    render(<UniversalSubmitForm />);

    expect(
      await screen.findByText(
        "This call cannot be rendered because one or more sections are missing logical ids.",
      ),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Submit" })).toBeDisabled();
  });

  it("uses metadata route labels when available", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url === "/api/bff/calls") {
        return new Response(
          JSON.stringify({
            calls: [
              {
                id: "call-1",
                code: "call_1",
                name: "Call 1",
                year: 2025,
                agency_short_name: "NWO",
              },
            ],
          }),
          { status: 200 },
        );
      }
      if (url === "/api/bff/calls/call_1/config") {
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
      if (url === "/api/bff/calls/call-1/nodes") {
        return new Response(
          JSON.stringify({
            nodes: [
              {
                id: "node-1",
                logical_id: "academic_profile",
                title: "Academic Profile",
                parent_node_id: null,
                node_type: "SECTION",
                order_index: 1,
                has_expectations: true,
              },
            ],
          }),
          { status: 200 },
        );
      }
      if (url === "/api/bff/calls/call_1/metadata") {
        return new Response(
          JSON.stringify({
            call_logical_id: "call_1",
            nodes: [
              {
                logical_id: "academic_profile",
                title: "Academic Profile from Metadata",
                parent_logical_id: null,
                word_limit_min: 0,
                word_limit_max: 500,
              },
            ],
            unknown_node_logical_ids: null,
          }),
          { status: 200 },
        );
      }
      return new Response(JSON.stringify({ ok: true }), { status: 200 });
    });
    vi.stubGlobal("fetch", fetchMock);
    render(<UniversalSubmitForm />);

    expect(await screen.findByLabelText("Academic Profile from Metadata")).toBeInTheDocument();
  });

  it("shows domain selector only for calls with configured domain options", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url === "/api/bff/calls") {
        return new Response(
          JSON.stringify({
            calls: [
              {
                id: "call-1",
                code: "nwo_veni_2025_preproposal",
                name: "NWO Veni",
                year: 2025,
                agency_short_name: "NWO",
              },
              {
                id: "call-2",
                code: "other_call",
                name: "Other Call",
                year: 2025,
                agency_short_name: "NWO",
              },
            ],
          }),
          { status: 200 },
        );
      }
      if (url === "/api/bff/calls/nwo_veni_2025_preproposal/config") {
        return new Response(
          JSON.stringify({
            call_logical_id: "nwo_veni_2025_preproposal",
            config_version: "1",
            ui_mode: "structured_nodes",
            expected_nodes: [],
          }),
          { status: 200 },
        );
      }
      if (url === "/api/bff/calls/other_call/config") {
        return new Response(
          JSON.stringify({
            call_logical_id: "other_call",
            config_version: "1",
            ui_mode: "structured_nodes",
            expected_nodes: [],
          }),
          { status: 200 },
        );
      }
      if (url === "/api/bff/calls/call-1/nodes" || url === "/api/bff/calls/call-2/nodes") {
        return new Response(
          JSON.stringify({
            nodes: [
              {
                id: "node-1",
                logical_id: "academic_profile",
                title: "Academic Profile",
                parent_node_id: null,
                node_type: "SECTION",
                order_index: 1,
                has_expectations: true,
              },
            ],
          }),
          { status: 200 },
        );
      }
      if (
        url === "/api/bff/calls/nwo_veni_2025_preproposal/metadata" ||
        url === "/api/bff/calls/other_call/metadata"
      ) {
        return new Response(
          JSON.stringify({
            call_logical_id: "call",
            nodes: [],
            unknown_node_logical_ids: null,
          }),
          { status: 200 },
        );
      }
      return new Response(JSON.stringify({ ok: true }), { status: 200 });
    });
    vi.stubGlobal("fetch", fetchMock);
    render(<UniversalSubmitForm />);

    expect(await screen.findByLabelText("Domain")).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Funding Call"), { target: { value: "call-2" } });
    await waitFor(() => {
      expect(screen.queryByLabelText("Domain")).not.toBeInTheDocument();
    });
  });

  it("submits selected domain and blocks on compliance 422", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url === "/api/bff/calls") {
        return new Response(
          JSON.stringify({
            calls: [
              {
                id: "call-1",
                code: "nwo_veni_2025_preproposal",
                name: "NWO Veni",
                year: 2025,
                agency_short_name: "NWO",
              },
            ],
          }),
          { status: 200 },
        );
      }
      if (url === "/api/bff/calls/nwo_veni_2025_preproposal/config") {
        return new Response(
          JSON.stringify({
            call_logical_id: "nwo_veni_2025_preproposal",
            config_version: "1",
            ui_mode: "structured_nodes",
            expected_nodes: [],
          }),
          { status: 200 },
        );
      }
      if (url === "/api/bff/calls/call-1/nodes") {
        return new Response(
          JSON.stringify({
            nodes: [
              {
                id: "node-1",
                logical_id: "academic_profile",
                title: "Academic Profile",
                parent_node_id: null,
                node_type: "SECTION",
                order_index: 1,
                has_expectations: true,
              },
            ],
          }),
          { status: 200 },
        );
      }
      if (url === "/api/bff/calls/nwo_veni_2025_preproposal/metadata") {
        return new Response(
          JSON.stringify({
            call_logical_id: "nwo_veni_2025_preproposal",
            nodes: [],
            unknown_node_logical_ids: null,
          }),
          { status: 200 },
        );
      }
      if (url === "/api/bff/check-compliance") {
        const body = JSON.parse(String(init?.body ?? "{}")) as { domain?: string | null };
        expect(body.domain).toBe("science_enw");
        return new Response(
          JSON.stringify({
            error: {
              code: "DOMAIN_INVALID",
              message: "domain is not recognized for this call.",
              details: { node_logical_ids: ["academic_profile"] },
            },
          }),
          { status: 422 },
        );
      }
      if (url === "/api/bff/structured-review") {
        return new Response(JSON.stringify({ review_id: "review-1" }), { status: 200 });
      }
      return new Response(JSON.stringify({ ok: true }), { status: 200 });
    });
    vi.stubGlobal("fetch", fetchMock);
    render(<UniversalSubmitForm />);

    fireEvent.change(await screen.findByLabelText("Academic Profile"), {
      target: { value: "content" },
    });
    fireEvent.change(screen.getByLabelText("Domain"), {
      target: { value: "science_enw" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Submit" }));

    expect(await screen.findByText("Submission blocked")).toBeInTheDocument();
    expect(
      fetchMock.mock.calls.some((call) => String(call[0]).includes("/api/bff/structured-review")),
    ).toBe(false);
  });

  it("keeps draft values isolated per selected call", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url === "/api/bff/calls") {
        return new Response(
          JSON.stringify({
            calls: [
              {
                id: "call-1",
                code: "nwo_veni_2025_preproposal",
                name: "NWO Veni",
                year: 2025,
                agency_short_name: "NWO",
              },
              {
                id: "call-2",
                code: "other_call",
                name: "Other",
                year: 2025,
                agency_short_name: "NWO",
              },
            ],
          }),
          { status: 200 },
        );
      }
      if (url.endsWith("/config")) {
        return new Response(
          JSON.stringify({
            call_logical_id: "call",
            config_version: "1",
            ui_mode: "structured_nodes",
            expected_nodes: [],
          }),
          { status: 200 },
        );
      }
      if (url === "/api/bff/calls/call-1/nodes" || url === "/api/bff/calls/call-2/nodes") {
        return new Response(
          JSON.stringify({
            nodes: [
              {
                id: "node-1",
                logical_id: "academic_profile",
                title: "Academic Profile",
                parent_node_id: null,
                node_type: "SECTION",
                order_index: 1,
                has_expectations: true,
              },
            ],
          }),
          { status: 200 },
        );
      }
      if (url.endsWith("/metadata")) {
        return new Response(
          JSON.stringify({
            call_logical_id: "call",
            nodes: [],
            unknown_node_logical_ids: null,
          }),
          { status: 200 },
        );
      }
      return new Response(JSON.stringify({ ok: true }), { status: 200 });
    });
    vi.stubGlobal("fetch", fetchMock);
    render(<UniversalSubmitForm />);

    fireEvent.change(await screen.findByLabelText("Academic Profile"), {
      target: { value: "draft for call 1" },
    });
    fireEvent.change(screen.getByLabelText("Funding Call"), { target: { value: "call-2" } });
    fireEvent.change(await screen.findByLabelText("Academic Profile"), {
      target: { value: "draft for call 2" },
    });
    fireEvent.change(screen.getByLabelText("Funding Call"), { target: { value: "call-1" } });

    expect(await screen.findByDisplayValue("draft for call 1")).toBeInTheDocument();
  });

  it("clears only active call draft on submit success", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url === "/api/bff/calls") {
        return new Response(
          JSON.stringify({
            calls: [
              {
                id: "call-1",
                code: "nwo_veni_2025_preproposal",
                name: "NWO Veni",
                year: 2025,
                agency_short_name: "NWO",
              },
              {
                id: "call-2",
                code: "other_call",
                name: "Other",
                year: 2025,
                agency_short_name: "NWO",
              },
            ],
          }),
          { status: 200 },
        );
      }
      if (url.endsWith("/config")) {
        return new Response(
          JSON.stringify({
            call_logical_id: "call",
            config_version: "1",
            ui_mode: "structured_nodes",
            expected_nodes: [],
          }),
          { status: 200 },
        );
      }
      if (url === "/api/bff/calls/call-1/nodes" || url === "/api/bff/calls/call-2/nodes") {
        return new Response(
          JSON.stringify({
            nodes: [
              {
                id: "node-1",
                logical_id: "academic_profile",
                title: "Academic Profile",
                parent_node_id: null,
                node_type: "SECTION",
                order_index: 1,
                has_expectations: true,
              },
            ],
          }),
          { status: 200 },
        );
      }
      if (url.endsWith("/metadata")) {
        return new Response(
          JSON.stringify({
            call_logical_id: "call",
            nodes: [],
            unknown_node_logical_ids: null,
          }),
          { status: 200 },
        );
      }
      if (url === "/api/bff/check-compliance") {
        return new Response(JSON.stringify({ is_compliant: true, errors: [], warnings: [] }), {
          status: 200,
        });
      }
      if (url === "/api/bff/structured-review") {
        return new Response(JSON.stringify({ review_id: "review-1" }), { status: 200 });
      }
      return new Response(JSON.stringify({ ok: true }), { status: 200 });
    });
    vi.stubGlobal("fetch", fetchMock);
    render(<UniversalSubmitForm />);

    fireEvent.change(await screen.findByLabelText("Academic Profile"), {
      target: { value: "draft for call 1" },
    });
    fireEvent.change(screen.getByLabelText("Funding Call"), { target: { value: "call-2" } });
    fireEvent.change(await screen.findByLabelText("Academic Profile"), {
      target: { value: "draft for call 2" },
    });

    fireEvent.click(screen.getByRole("button", { name: "Submit" }));
    await waitFor(() => {
      expect(push).toHaveBeenCalled();
    });

    expect(window.localStorage.getItem("draft_universal_submit_call-2_v1")).toBeNull();
    expect(window.localStorage.getItem("draft_universal_submit_call-1_v1")).not.toBeNull();
  });

  it("warning bypass modal gates submit until confirmation", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url === "/api/bff/calls") {
        return new Response(
          JSON.stringify({
            calls: [
              {
                id: "call-1",
                code: "nwo_veni_2025_preproposal",
                name: "NWO Veni",
                year: 2025,
                agency_short_name: "NWO",
              },
            ],
          }),
          { status: 200 },
        );
      }
      if (url === "/api/bff/calls/nwo_veni_2025_preproposal/config") {
        return new Response(
          JSON.stringify({
            call_logical_id: "nwo_veni_2025_preproposal",
            config_version: "1",
            ui_mode: "structured_nodes",
            expected_nodes: [],
          }),
          { status: 200 },
        );
      }
      if (url === "/api/bff/calls/call-1/nodes") {
        return new Response(
          JSON.stringify({
            nodes: [
              {
                id: "node-1",
                logical_id: "academic_profile",
                title: "Academic Profile",
                parent_node_id: null,
                node_type: "SECTION",
                order_index: 1,
                has_expectations: true,
              },
            ],
          }),
          { status: 200 },
        );
      }
      if (url === "/api/bff/calls/nwo_veni_2025_preproposal/metadata") {
        return new Response(
          JSON.stringify({
            call_logical_id: "nwo_veni_2025_preproposal",
            nodes: [],
            unknown_node_logical_ids: null,
          }),
          { status: 200 },
        );
      }
      if (url === "/api/bff/check-compliance") {
        return new Response(
          JSON.stringify({
            is_compliant: false,
            errors: [
              {
                node_logical_id: "academic_profile",
                rule_id: "word_limit_max",
                severity: "ERROR",
                actual: "101",
                expected: "100",
                message: "Maximum word limit is 100.",
                is_blocking: true,
              },
            ],
            warnings: [],
          }),
          { status: 200 },
        );
      }
      if (url === "/api/bff/structured-review") {
        return new Response(JSON.stringify({ review_id: "review-1" }), { status: 200 });
      }
      return new Response(JSON.stringify({ ok: true }), { status: 200 });
    });
    vi.stubGlobal("fetch", fetchMock);
    render(<UniversalSubmitForm />);

    fireEvent.change(await screen.findByLabelText("Academic Profile"), {
      target: { value: "content" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Submit" }));
    expect(await screen.findByText("Submit with warnings?")).toBeInTheDocument();
    expect(
      fetchMock.mock.calls.some((call) => String(call[0]).includes("/api/bff/structured-review")),
    ).toBe(false);

    fireEvent.click(screen.getByRole("button", { name: "Submit Anyway" }));
    await waitFor(() => {
      expect(
        fetchMock.mock.calls.some((call) => String(call[0]).includes("/api/bff/structured-review")),
      ).toBe(true);
    });
  });

  it("does not create submit nodes from unmatched metadata", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url === "/api/bff/calls") {
        return new Response(
          JSON.stringify({
            calls: [
              {
                id: "call-1",
                code: "nwo_veni_2025_preproposal",
                name: "NWO Veni",
                year: 2025,
                agency_short_name: "NWO",
              },
            ],
          }),
          { status: 200 },
        );
      }
      if (url === "/api/bff/calls/nwo_veni_2025_preproposal/config") {
        return new Response(
          JSON.stringify({
            call_logical_id: "nwo_veni_2025_preproposal",
            config_version: "1",
            ui_mode: "structured_nodes",
            expected_nodes: [],
          }),
          { status: 200 },
        );
      }
      if (url === "/api/bff/calls/call-1/nodes") {
        return new Response(
          JSON.stringify({
            nodes: [
              {
                id: "node-1",
                logical_id: "academic_profile",
                title: "Academic Profile",
                parent_node_id: null,
                node_type: "SECTION",
                order_index: 1,
                has_expectations: true,
              },
            ],
          }),
          { status: 200 },
        );
      }
      if (url === "/api/bff/calls/nwo_veni_2025_preproposal/metadata") {
        return new Response(
          JSON.stringify({
            call_logical_id: "nwo_veni_2025_preproposal",
            nodes: [
              {
                logical_id: "not_a_real_node",
                title: "Should not be rendered",
                parent_logical_id: null,
                word_limit_min: null,
                word_limit_max: null,
              },
            ],
            unknown_node_logical_ids: null,
          }),
          { status: 200 },
        );
      }
      if (url === "/api/bff/check-compliance") {
        return new Response(JSON.stringify({ is_compliant: true, errors: [], warnings: [] }), {
          status: 200,
        });
      }
      if (url === "/api/bff/structured-review") {
        const body = JSON.parse(String(init?.body ?? "{}")) as { nodes?: Array<{ node_logical_id: string }> };
        expect(body.nodes).toEqual([{ node_logical_id: "academic_profile", text: "content" }]);
        return new Response(JSON.stringify({ review_id: "review-1" }), { status: 200 });
      }
      return new Response(JSON.stringify({ ok: true }), { status: 200 });
    });
    vi.stubGlobal("fetch", fetchMock);
    render(<UniversalSubmitForm />);

    fireEvent.change(await screen.findByLabelText("Academic Profile"), {
      target: { value: "content" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Submit" }));
    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/bff/structured-review",
        expect.objectContaining({ method: "POST" }),
      );
    });
  });

  it("emits telemetry for gating summary and submit outcomes", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url === "/api/bff/calls") {
        return new Response(
          JSON.stringify({
            calls: [
              {
                id: "call-1",
                code: "nwo_veni_2025_preproposal",
                name: "NWO Veni",
                year: 2025,
                agency_short_name: "NWO",
              },
            ],
          }),
          { status: 200 },
        );
      }
      if (url.endsWith("/config")) {
        return new Response(
          JSON.stringify({
            call_logical_id: "nwo_veni_2025_preproposal",
            config_version: "1",
            ui_mode: "structured_nodes",
            expected_nodes: [],
          }),
          { status: 200 },
        );
      }
      if (url.endsWith("/nodes")) {
        return new Response(
          JSON.stringify({
            nodes: [
              {
                id: "node-1",
                logical_id: "academic_profile",
                title: "Academic Profile",
                parent_node_id: null,
                node_type: "SECTION",
                order_index: 1,
                has_expectations: true,
              },
            ],
          }),
          { status: 200 },
        );
      }
      if (url.endsWith("/metadata")) {
        return new Response(
          JSON.stringify({
            call_logical_id: "nwo_veni_2025_preproposal",
            nodes: [],
            unknown_node_logical_ids: null,
          }),
          { status: 200 },
        );
      }
      if (url === "/api/bff/check-compliance") {
        return new Response(JSON.stringify({ is_compliant: true, errors: [], warnings: [] }), {
          status: 200,
        });
      }
      if (url === "/api/bff/structured-review") {
        return new Response(JSON.stringify({ review_id: "review-1" }), { status: 200 });
      }
      return new Response(JSON.stringify({ ok: true }), { status: 200 });
    });
    vi.stubGlobal("fetch", fetchMock);
    render(<UniversalSubmitForm />);

    fireEvent.change(await screen.findByLabelText("Academic Profile"), {
      target: { value: "content" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Submit" }));

    await waitFor(() => {
      expect(console.info).toHaveBeenCalledWith(
        "universal_submit.gating_summary",
        expect.objectContaining({ total_calls: 1 }),
      );
      expect(console.info).toHaveBeenCalledWith(
        "universal_submit.submit_outcome",
        expect.objectContaining({ outcome: "success" }),
      );
    });
  });
});
