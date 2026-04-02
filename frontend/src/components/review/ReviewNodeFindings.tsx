// frontend/src/components/review/ReviewNodeFindings.tsx
import type { ReviewedNodeSummary } from "@/lib/bff/types";

import { ScoreBadge } from "./ScoreBadge";

type ReviewNodeFindingsProps = {
  reviewedNode: ReviewedNodeSummary;
};

function formatAssessmentStatusLabel(
  assessmentStatus: ReviewedNodeSummary["findings"][number]["assessment_status"],
): string {
  switch (assessmentStatus) {
    case "REQUIREMENTS_MET":
      return "Requirements met";
    case "NOT_ASSESSABLE":
      return "Not assessable";
    case "ASSESSED":
    default:
      return "Assessed";
  }
}

export function ReviewNodeFindings({
  reviewedNode,
}: ReviewNodeFindingsProps) {
  return (
    <section
      className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-4"
      aria-labelledby={`heading-reviewed-node-${reviewedNode.proposal_node_id}`}
    >
      <h2
        id={`heading-reviewed-node-${reviewedNode.proposal_node_id}`}
        className="text-base font-semibold text-[var(--color-foreground)]"
      >
        Reviewed section: {reviewedNode.proposal_node_title}
      </h2>
      <div className="mt-3 grid gap-4">
        {reviewedNode.findings.map((finding, index) => (
          <article
            key={finding.finding_id}
            className="overflow-hidden rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm"
          >
            <header className="flex flex-col gap-4 border-b border-[var(--color-border)] bg-[var(--color-background)] px-6 py-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.08em] text-[var(--color-muted-foreground)]">
                  Finding {index + 1}
                </p>
                <h3 className="text-lg font-semibold text-[var(--color-foreground)]">
                  {finding.evaluation_element}
                </h3>
                <p className="mt-1 text-xs text-[var(--color-muted-foreground)]">
                  Evaluation criterion: {finding.evaluation_criterion}
                </p>
                <p className="mt-1 text-xs font-medium uppercase tracking-[0.08em] text-[var(--color-muted-foreground)]">
                  Evaluation element: {finding.evaluation_element}
                </p>
              </div>
              <div className="flex flex-col items-start gap-2 sm:items-end">
                <ScoreBadge rating={finding.severity} />
                <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.08em] text-slate-700">
                  {formatAssessmentStatusLabel(finding.assessment_status)}
                </span>
              </div>
            </header>
            <div className="grid gap-4 px-6 py-5 text-sm text-[var(--color-foreground)]">
              <section aria-label="Issue summary">
                <p className="text-xs font-semibold uppercase tracking-[0.08em] text-[var(--color-muted-foreground)]">
                  Issue summary
                </p>
                <p className="mt-2 whitespace-pre-wrap">{finding.issue_summary}</p>
              </section>
              <section aria-label="Evidence basis">
                <p className="text-xs font-semibold uppercase tracking-[0.08em] text-[var(--color-muted-foreground)]">
                  Evidence basis
                </p>
                <p className="mt-2 whitespace-pre-wrap">{finding.evidence_basis}</p>
              </section>
              <section aria-label="Actionable feedback">
                <p className="text-xs font-semibold uppercase tracking-[0.08em] text-[var(--color-muted-foreground)]">
                  Actionable feedback
                </p>
                <p className="mt-2 whitespace-pre-wrap">
                  {finding.actionable_feedback}
                </p>
              </section>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
