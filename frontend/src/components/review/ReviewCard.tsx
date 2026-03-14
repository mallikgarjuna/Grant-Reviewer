// frontend/src/components/review/ReviewCard.tsx
import { ReviewRating } from "@/lib/bff/types";
import { ScoreBadge } from "./ScoreBadge";

interface ReviewCardProps {
  cardId?: string;
  index: number;
  criterion: string;
  description?: string | null;
  evaluationElementName: string;
  rating: ReviewRating;
  feedback: string;
  synthesizedCompanionText?: string | null;
}

function buildFeedbackBullets(feedback: string): string[] {
  const normalizedParts = feedback
    .split("\n")
    .map((part) => part.trim())
    .filter((part) => part.length > 0);

  if (normalizedParts.length > 1) {
    return normalizedParts;
  }

  return feedback
    .split(/(?<=[.!?])\s+(?=[A-Z0-9])/)
    .map((part) => part.trim())
    .filter((part) => part.length > 0);
}

export function ReviewCard({
  cardId,
  index,
  criterion,
  description,
  evaluationElementName,
  rating,
  feedback,
  synthesizedCompanionText,
}: ReviewCardProps) {
  const hasSynthesizedCompanionText =
    typeof synthesizedCompanionText === "string" &&
    synthesizedCompanionText.trim().length > 0;
  const feedbackBullets = buildFeedbackBullets(feedback);
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
        <section aria-label="Deterministic feedback">
          <p className="text-xs font-semibold uppercase tracking-[0.08em] text-[var(--color-muted-foreground)]">
            Deterministic feedback
          </p>
          <ul className="mt-3 list-disc space-y-2 pl-5 text-sm text-[var(--color-foreground)]">
            {feedbackBullets.map((bullet) => (
              <li key={bullet} className="whitespace-pre-wrap">
                {bullet}
              </li>
            ))}
          </ul>
        </section>
        {hasSynthesizedCompanionText ? (
          <section
            aria-label="LLM companion guidance"
            className="mt-4 rounded-lg border border-sky-200 bg-sky-50 px-4 py-3"
          >
            <p className="text-xs font-semibold uppercase tracking-[0.08em] text-sky-800">
              LLM companion guidance
            </p>
            <p className="mt-2 whitespace-pre-wrap text-sm text-sky-950">
              {synthesizedCompanionText}
            </p>
          </section>
        ) : null}
      </div>
    </article>
  );
}
