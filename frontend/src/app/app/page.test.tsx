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
  it("renders hardcoded Veni structured form shell", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        new Response(
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
        ),
      ),
    );

    render(<AppSubmitPage />);

    expect(await screen.findByLabelText("Academic Profile")).toBeInTheDocument();
    expect(screen.getByLabelText("Key Outputs")).toBeInTheDocument();
    expect(screen.getByLabelText("Research Idea")).toBeInTheDocument();
  });
});
