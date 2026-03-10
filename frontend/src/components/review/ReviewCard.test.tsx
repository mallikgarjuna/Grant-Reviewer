// frontend/src/components/review/ReviewCard.test.tsx
import "@testing-library/jest-dom/vitest";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ReviewCard } from "@/components/review/ReviewCard";

describe("ReviewCard", () => {
  it("renders ancestor breadcrumb path from reviewed section context", () => {
    render(
      <ReviewCard
        index={1}
        criterion="Excellence"
        reviewedSectionLabel="Part B / Part B1 / Proposal Summary"
        evaluationElementName="Novelty"
        rating="SUCCESS"
        feedback="Strong novelty and clear hypothesis."
      />,
    );

    expect(
      screen.getByText(
        "Section breadcrumb: Part B > Part B1 > Proposal Summary",
      ),
    ).toBeInTheDocument();
  });

  it("does not render breadcrumb when section context has no ancestors", () => {
    render(
      <ReviewCard
        index={2}
        criterion="Feasibility"
        reviewedSectionLabel="Proposal Summary"
        evaluationElementName="Work plan"
        rating="WARNING"
        feedback="Timeline is partially underspecified."
      />,
    );

    expect(screen.queryByText(/Section breadcrumb:/)).toBeNull();
  });
});
