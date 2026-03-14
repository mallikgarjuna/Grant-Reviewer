// frontend/src/components/review/ReviewCard.tsx
import { ReviewRating } from "@/lib/bff/types";
import { ScoreBadge } from "./ScoreBadge";

interface ReviewCardProps {
  cardId?: string;
  index: number;
  criterion: string;
  description?: string | null;
  reviewedSectionLabel?: string | null;
  evaluationElementName: string;
  expectationGuidanceNote?: string | null;
  rating: ReviewRating;
  feedback: string;
  synthesizedCompanionText?: string | null;
  assessmentStatus?: "ASSESSED" | "NOT_ASSESSABLE" | null;
  notAssessableReason?: string | null;
  sourceBasisLabel?: string | null;
  sourceBasisState?: "available" | "unavailable" | "legacy_fallback";
  supportingEvidenceDefaultOpen?: boolean;
}

function sourceBasisLine(
  sourceBasisState: ReviewCardProps["sourceBasisState"],
  sourceBasisLabel: ReviewCardProps["sourceBasisLabel"],
): string {
  if (sourceBasisState === "available" && sourceBasisLabel) {
    return `Official source basis: ${sourceBasisLabel}`;
  }
  if (sourceBasisState === "legacy_fallback") {
    return "Official source basis: unavailable (legacy fallback).";
  }
  return "Official source basis: unavailable.";
}

function buildBreadcrumbPath(reviewedSectionLabel?: string | null): string | null {
  if (!reviewedSectionLabel) {
    return null;
  }
  const parts = reviewedSectionLabel
    .split(/[/>]/)
    .map((part) => part.trim())
    .filter((part) => part.length > 0);
  if (parts.length <= 1) {
    return null;
  }
  return parts.join(" > ");
}

export function ReviewCard({
  cardId,
  index,
  criterion,
  description,
  reviewedSectionLabel,
  evaluationElementName,
  expectationGuidanceNote,
  rating,
  feedback,
  synthesizedCompanionText,
  assessmentStatus,
  notAssessableReason,
  sourceBasisLabel,
  sourceBasisState,
  supportingEvidenceDefaultOpen = false,
}: ReviewCardProps) {
  const breadcrumbPath = buildBreadcrumbPath(reviewedSectionLabel);
  const hasSynthesizedCompanionText =
    typeof synthesizedCompanionText === "string" &&
    synthesizedCompanionText.trim().length > 0;
  const hasSupportingEvidence =
    Boolean(reviewedSectionLabel) ||
    Boolean(breadcrumbPath) ||
    Boolean(expectationGuidanceNote) ||
    assessmentStatus === "NOT_ASSESSABLE" ||
    Boolean(sourceBasisState);
  return (
    <article
      className="overflow-hidden rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm transition-all hover:shadow-md"
      data-card-id={cardId}
      data-testid={cardId ? `review-card-${cardId}` : undefined}
    >
      <header className="flex flex-col gap-4 border-b border-[var(--color-border)] bg-[var(--color-background)] px-6 py-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.08em] text-[var(--color-muted-foreground)]">
            Finding {index}
          </p>
          <h3 className="text-lg font-semibold text-[var(--color-foreground)]">
            {evaluationElementName}
          </h3>
          <p className="mt-1 text-xs text-[var(--color-muted-foreground)]">
            Evaluation criterion: {criterion}
          </p>
          {description && criterion !== description && (
            <p className="mt-1 text-sm text-[var(--color-muted-foreground)]">
              {description}
            </p>
          )}
        </div>
        <div className="flex-shrink-0">
          <ScoreBadge rating={rating} />
        </div>
      </header>
      <div className="px-6 py-5">
        <div className="prose prose-sm max-w-none text-[var(--color-foreground)] dark:prose-invert">
          {/* We treat feedback as pre-formatted text or markdown if supported later */}
          <p className="whitespace-pre-wrap">{feedback}</p>
        </div>
        {hasSynthesizedCompanionText ? (
          <div className="mt-4 rounded-lg border border-sky-200 bg-sky-50 px-4 py-3">
            <p className="text-xs font-semibold uppercase tracking-[0.08em] text-sky-800">
              Additive companion guidance
            </p>
            <p className="mt-2 whitespace-pre-wrap text-sm text-sky-950">
              {synthesizedCompanionText}
            </p>
          </div>
        ) : null}
        {hasSupportingEvidence ? (
          <details
            className="mt-4 rounded-lg border border-[var(--color-border)] bg-[var(--color-background)] px-4 py-3"
            open={supportingEvidenceDefaultOpen}
          >
            <summary className="cursor-pointer text-sm font-medium text-[var(--color-foreground)]">
              Supporting evidence
            </summary>
            <div className="mt-3 space-y-2 text-xs text-[var(--color-muted-foreground)]">
              {reviewedSectionLabel ? (
                <p>Reviewed section context: {reviewedSectionLabel}</p>
              ) : null}
              {breadcrumbPath ? <p>Section breadcrumb: {breadcrumbPath}</p> : null}
              {expectationGuidanceNote ? (
                <p>Reviewer focus: {expectationGuidanceNote}</p>
              ) : null}
              {assessmentStatus === "NOT_ASSESSABLE" ? (
                <p>
                  Status: Not assessable
                  {notAssessableReason ? ` (${notAssessableReason})` : ""}
                </p>
              ) : null}
              <p>{sourceBasisLine(sourceBasisState, sourceBasisLabel)}</p>
            </div>
          </details>
        ) : null}
      </div>
    </article>
  );
}
