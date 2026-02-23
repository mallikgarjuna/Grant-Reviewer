import "@testing-library/jest-dom/vitest";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import ReviewDetailPage from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  useParams: () => ({ reviewId: "review-1" }),
  useSearchParams: () => ({
    get: (key: string) => (key === "submitted_nodes" ? "academic_profile" : null),
  }),
}));

describe("ReviewDetailPage", () => {
  it("shows coverage summary for reviewed and not reviewed sections", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url.includes("/api/bff/reviews/review-1")) {
          return new Response(
            JSON.stringify({
              review: {
                id: "review-1",
                status: "COMPLETED",
                overall_rating: "GOOD",
                overall_summary: "Structured review completed with findings.",
              },
              cards: [
                {
                  id: "card-1",
                  node_expectation_id: "exp-1",
                  criterion: "Quality",
                  criterion_description: "Quality criterion",
                  rating: "GOOD",
                  feedback_text: "Feedback text",
                },
              ],
            }),
            { status: 200 },
          );
        }
        return new Response(JSON.stringify({ error: { code: "NOT_FOUND", message: "Not found" } }), {
          status: 404,
        });
      }),
    );

    render(<ReviewDetailPage />);

    expect(await screen.findByText("Coverage summary")).toBeInTheDocument();
    expect(screen.getByText(/Reviewed sections:/)).toHaveTextContent(
      "Reviewed sections: 2a. Academic Profile",
    );
    expect(screen.getByText(/Not reviewed sections:/)).toHaveTextContent(
      "Not reviewed sections: 2b. Key Outputs, 3. Research Idea",
    );
  });
});
