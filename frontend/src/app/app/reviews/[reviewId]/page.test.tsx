import "@testing-library/jest-dom/vitest";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import ReviewDetailPage from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  useParams: () => ({ reviewId: "review-1" }),
  useSearchParams: () => ({
    get: (key: string) => (key === "submitted_nodes" ? "academic_profile,key_outputs" : null),
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
                  id: "card-2",
                  node_expectation_id: "exp-2",
                  node_logical_id: "key_outputs",
                  node_title: "Key outputs",
                  criterion: "Quality",
                  criterion_description: "Quality criterion",
                  evaluation_element_name: "Key-output quality",
                  expectation_guidance_note: "Show output relevance.",
                  rating: "GOOD",
                  feedback_text: "Second feedback",
                },
                {
                  id: "card-1",
                  node_expectation_id: "exp-1",
                  node_logical_id: "academic_profile",
                  node_title: "Academic profile",
                  criterion: "Quality",
                  criterion_description: "Quality criterion",
                  evaluation_element_name: "Peer-exceeding quality",
                  expectation_guidance_note: "Provide concrete evidence.",
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
      "Reviewed sections: 2a. Academic Profile, 2b. Key Outputs",
    );
    expect(screen.getByText(/Not reviewed sections:/)).toHaveTextContent(
      "Not reviewed sections: 3. Research Idea",
    );
    expect(screen.getAllByText("Finding 1")).toHaveLength(2);
    expect(screen.getByText("Evaluation element: Peer-exceeding quality")).toBeInTheDocument();
    expect(screen.getByText("Reviewer focus: Provide concrete evidence.")).toBeInTheDocument();
    expect(screen.getByText("Reviewed section: 2a. Academic Profile")).toBeInTheDocument();
    expect(screen.getByText("Reviewed section: 2b. Key Outputs")).toBeInTheDocument();
    expect(screen.getByText("Not reviewed section: 3. Research Idea")).toBeInTheDocument();
    expect(
      screen.getAllByText(
        "No text was submitted for this section in this review, so no evaluation cards were generated.",
      ),
    ).toHaveLength(1);
    const pageText = document.body.textContent ?? "";
    expect(pageText.indexOf("Reviewed section: 2a. Academic Profile")).toBeLessThan(
      pageText.indexOf("Reviewed section: 2b. Key Outputs"),
    );
  });
});
