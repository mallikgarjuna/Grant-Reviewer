import { ReviewRating } from "@/lib/bff/types";
import { ScoreBadge } from "./ScoreBadge";

interface ReviewCardProps {
  index: number;
  criterion: string;
  description?: string | null;
  evaluationElementName: string;
  expectationGuidanceNote?: string | null;
  rating: ReviewRating;
  feedback: string;
  assessmentStatus?: "ASSESSED" | "NOT_ASSESSABLE" | null;
  notAssessableReason?: string | null;
}

export function ReviewCard({
  index,
  criterion,
  description,
  evaluationElementName,
  expectationGuidanceNote,
  rating,
  feedback,
  assessmentStatus,
  notAssessableReason,
}: ReviewCardProps) {
  return (
    <article className="overflow-hidden rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm transition-all hover:shadow-md">
      <header className="flex flex-col gap-4 border-b border-[var(--color-border)] bg-[var(--color-background)] px-6 py-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.08em] text-[var(--color-muted-foreground)]">
            Finding {index}
          </p>
          <h3 className="text-lg font-semibold text-[var(--color-foreground)]">
            {criterion}
          </h3>
          {description && (
            <p className="mt-1 text-sm text-[var(--color-muted-foreground)]">
              {description}
            </p>
          )}
          <p className="mt-1 text-xs text-[var(--color-muted-foreground)]">
            Evaluation element: {evaluationElementName}
          </p>
          {expectationGuidanceNote ? (
            <p className="mt-1 text-xs text-[var(--color-muted-foreground)]">
              Reviewer focus: {expectationGuidanceNote}
            </p>
          ) : null}
          {assessmentStatus === "NOT_ASSESSABLE" ? (
            <p className="mt-1 text-xs font-medium text-[var(--color-muted-foreground)]">
              Status: Not assessable
              {notAssessableReason ? ` (${notAssessableReason})` : ""}
            </p>
          ) : null}
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
      </div>
    </article>
  );
}
