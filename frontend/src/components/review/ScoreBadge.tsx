import { ReviewRating } from "@/lib/bff/types";

interface ScoreBadgeProps {
  rating: ReviewRating;
}

export function ScoreBadge({ rating }: ScoreBadgeProps) {
  const config: Record<ReviewRating, { label: string; bg: string; text: string; dots: number }> = {
    SUCCESS: { label: "Excellent (5/5)", bg: "bg-green-100", text: "text-green-800", dots: 5 },
    NOTE: { label: "Good (4/5)", bg: "bg-teal-100", text: "text-teal-800", dots: 4 },
    WARNING: { label: "Fair (3/5)", bg: "bg-yellow-100", text: "text-yellow-800", dots: 3 },
    CRITICAL: { label: "Needs Improvement (1/5)", bg: "bg-red-100", text: "text-red-800", dots: 1 },
  };

  const { label, bg, text, dots } = config[rating] || config.NOTE;

  return (
    <div className={`inline-flex items-center gap-2 rounded-full px-3 py-1 ${bg} ${text}`}>
      <div className="flex gap-0.5">
        {[1, 2, 3, 4, 5].map((i) => (
          <div
            key={i}
            className={`h-2 w-2 rounded-full ${i <= dots ? "bg-current opacity-100" : "bg-current opacity-20"}`}
          />
        ))}
      </div>
      <span className="text-xs font-bold uppercase tracking-wide">{label}</span>
    </div>
  );
}
