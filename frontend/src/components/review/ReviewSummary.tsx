import { ReviewSummary as ReviewSummaryType } from "@/lib/bff/types";

interface ReviewSummaryProps {
  summary: ReviewSummaryType;
}

export function ReviewSummary({ summary }: ReviewSummaryProps) {
  const { overall_summary, status } = summary;

  if (!overall_summary) return null;

  return (
    <div className="mb-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] bg-opacity-50 p-6">
      <h2 className="text-lg font-semibold text-[var(--color-foreground)]">Review Summary</h2>
      <div className="mt-4 prose prose-sm max-w-none text-[var(--color-foreground)] dark:prose-invert">
        <p className="whitespace-pre-wrap">{overall_summary}</p>
      </div>
    </div>
  );
}
