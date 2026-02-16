"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import type { ApiError, ReviewListItem } from "@/lib/bff/types";

type PageState =
  | { kind: "loading" }
  | { kind: "error"; error: ApiError }
  | { kind: "loaded"; reviews: ReviewListItem[] };

function StatusBadge({ status }: { status: string }) {
  let bg: string;
  let fg: string;
  switch (status) {
    case "COMPLETED":
      bg = "var(--color-success-muted, #d1fae5)";
      fg = "var(--color-success-fg, #065f46)";
      break;
    case "FAILED":
      bg = "var(--color-destructive-muted, #fee2e2)";
      fg = "var(--color-destructive-fg, #991b1b)";
      break;
    default:
      bg = "var(--color-surface-muted)";
      fg = "var(--color-muted-foreground)";
  }
  return (
    <span
      className="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium"
      style={{ backgroundColor: bg, color: fg }}
    >
      {status}
    </span>
  );
}

function RatingPill({ rating }: { rating: string | null }) {
  if (!rating) return null;
  const labels: Record<string, { label: string; bg: string; fg: string }> = {
    SUCCESS: {
      label: "Strong",
      bg: "var(--color-success-muted, #d1fae5)",
      fg: "var(--color-success-fg, #065f46)",
    },
    NOTE: {
      label: "Adequate",
      bg: "var(--color-surface-muted)",
      fg: "var(--color-muted-foreground)",
    },
    WARNING: {
      label: "Needs Work",
      bg: "var(--color-warning-muted, #fef3c7)",
      fg: "var(--color-warning-fg, #92400e)",
    },
    CRITICAL: {
      label: "Weak",
      bg: "var(--color-destructive-muted, #fee2e2)",
      fg: "var(--color-destructive-fg, #991b1b)",
    },
  };
  const info = labels[rating] ?? { label: rating, bg: "var(--color-surface-muted)", fg: "var(--color-muted-foreground)" };
  return (
    <span
      className="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium"
      style={{ backgroundColor: info.bg, color: info.fg }}
    >
      {info.label}
    </span>
  );
}

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}

export default function ReviewsListPage() {
  const [state, setState] = useState<PageState>({ kind: "loading" });

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const res = await fetch("/api/bff/reviews");
        if (!res.ok) {
          let error: ApiError;
          try {
            const parsed = await res.json();
            error = parsed.error ?? {
              code: "INTERNAL_ERROR",
              message: "Failed to load reviews.",
              details: {},
              status: res.status,
            };
          } catch {
            error = {
              code: "INTERNAL_ERROR",
              message: "Failed to load reviews.",
              details: {},
              status: res.status,
            };
          }
          if (!cancelled) setState({ kind: "error", error });
          return;
        }
        const data = await res.json();
        if (!cancelled) setState({ kind: "loaded", reviews: data.reviews ?? [] });
      } catch {
        if (!cancelled)
          setState({
            kind: "error",
            error: {
              code: "NETWORK_ERROR",
              message: "Unable to reach the server.",
              details: {},
              status: 0,
            },
          });
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <main className="mx-auto max-w-5xl px-6 py-10 md:px-10">
      <div className="mb-8 flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-[var(--color-foreground)]">
            My Reviews
          </h1>
          <p className="mt-1 text-sm text-[var(--color-muted-foreground)]">
            Your past AI-powered proposal reviews.
          </p>
        </div>
        <Link
          className="inline-flex h-9 items-center rounded-[var(--radius-md)] bg-[var(--color-primary)] px-4 text-sm font-medium text-[var(--color-primary-foreground)] transition hover:opacity-90"
          href="/app"
        >
          New Review
        </Link>
      </div>

      {/* Loading */}
      {state.kind === "loading" && (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-20 animate-pulse rounded-[var(--radius-lg)] bg-[var(--color-surface-muted)]"
            />
          ))}
        </div>
      )}

      {/* Error */}
      {state.kind === "error" && (
        <div className="rounded-[var(--radius-lg)] border border-[var(--color-destructive-muted)] bg-[var(--color-destructive-muted)]/30 px-5 py-4 text-sm text-[var(--color-foreground)]">
          <p className="font-semibold">Error loading reviews</p>
          <p className="mt-1 text-[var(--color-muted-foreground)]">
            {state.error.message}
          </p>
        </div>
      )}

      {/* Empty */}
      {state.kind === "loaded" && state.reviews.length === 0 && (
        <div className="flex flex-col items-center rounded-[var(--radius-lg)] border border-dashed border-[var(--color-border)] px-6 py-16 text-center">
          <p className="text-lg font-medium text-[var(--color-foreground)]">
            No reviews yet
          </p>
          <p className="mt-1 text-sm text-[var(--color-muted-foreground)]">
            Submit a proposal snippet to get your first AI-powered review.
          </p>
          <Link
            className="mt-6 inline-flex h-9 items-center rounded-[var(--radius-md)] bg-[var(--color-primary)] px-4 text-sm font-medium text-[var(--color-primary-foreground)] transition hover:opacity-90"
            href="/app"
          >
            Start a Review
          </Link>
        </div>
      )}

      {/* Review List */}
      {state.kind === "loaded" && state.reviews.length > 0 && (
        <ul className="space-y-3">
          {state.reviews.map((review) => (
            <li key={review.id}>
              <Link
                className="group flex items-center justify-between rounded-[var(--radius-lg)] border border-[var(--color-border)] bg-[var(--color-surface)] px-5 py-4 transition hover:border-[var(--color-primary)]/40 hover:shadow-sm"
                href={`/app/reviews/${review.id}`}
              >
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-[var(--color-foreground)] truncate">
                      {review.call_name}
                    </span>
                    <span className="text-xs text-[var(--color-muted-foreground)]">
                      ·
                    </span>
                    <span className="text-sm text-[var(--color-muted-foreground)] truncate">
                      {review.node_title}
                    </span>
                  </div>
                  <div className="mt-1.5 flex items-center gap-2">
                    <StatusBadge status={review.status} />
                    <RatingPill rating={review.overall_rating} />
                    <span className="text-xs text-[var(--color-muted-foreground)]">
                      {formatDate(review.created_at)}
                    </span>
                  </div>
                </div>
                <svg
                  className="ml-4 h-4 w-4 shrink-0 text-[var(--color-muted-foreground)] transition group-hover:text-[var(--color-foreground)]"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth={2}
                  viewBox="0 0 24 24"
                >
                  <path d="M9 5l7 7-7 7" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
