import "@testing-library/jest-dom/vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import AppSubmitPage from "./page";

const push = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push,
  }),
}));

describe("AppSubmitPage", () => {
  it("renders universal submit shell", async () => {
    push.mockReset();
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url === "/api/bff/calls") {
          return new Response(
            JSON.stringify({
              calls: [
                {
                  id: "veni-call-id",
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
        if (url === "/api/bff/calls/veni-call-id/nodes") {
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
        return new Response(JSON.stringify({ is_compliant: true, errors: [], warnings: [] }), {
          status: 200,
        });
      }),
    );

    render(<AppSubmitPage />);

    expect(await screen.findByLabelText("Academic Profile")).toBeInTheDocument();
    expect(screen.queryByLabelText("Key Outputs")).not.toBeInTheDocument();
  });

  it("routes to reviews history detail path after submit success", async () => {
    push.mockReset();

    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url === "/api/bff/calls") {
          return new Response(
            JSON.stringify({
              calls: [
                {
                  id: "veni-call-id",
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
              domain_options: [],
            }),
            { status: 200 },
          );
        }
        if (url === "/api/bff/calls/veni-call-id/nodes") {
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
          return new Response(JSON.stringify({ is_compliant: true, errors: [], warnings: [] }), {
            status: 200,
          });
        }
        if (url === "/api/bff/structured-review") {
          return new Response(JSON.stringify({ review_id: "review-history-1" }), { status: 200 });
        }
        return new Response(JSON.stringify({ ok: true }), { status: 200 });
      }),
    );

    render(<AppSubmitPage />);

    fireEvent.change(await screen.findByLabelText("Academic Profile"), {
      target: { value: "content" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Submit" }));

    await waitFor(() => {
      expect(push).toHaveBeenCalledWith(
        "/app/reviews/review-history-1?submitted_nodes=academic_profile",
      );
    });
  });
});
