import "@testing-library/jest-dom/vitest";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import AppSubmitPage from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}));

describe("AppSubmitPage", () => {
  it("renders universal submit shell", async () => {
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
        return new Response(JSON.stringify({ is_compliant: true, errors: [], warnings: [] }), {
          status: 200,
        });
      }),
    );

    render(<AppSubmitPage />);

    expect(await screen.findByLabelText("Academic Profile")).toBeInTheDocument();
    expect(screen.queryByLabelText("Key Outputs")).not.toBeInTheDocument();
  });
});
