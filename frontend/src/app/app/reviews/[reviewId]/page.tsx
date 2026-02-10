"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import {
  createNewReviewAttempt,
  getStoredReviewAttempt,
} from "@/lib/review-attempt";
import type { ApiError, ReviewDetailResponse } from "@/lib/bff/types";

type ApiErrorEnvelope = {
  error?: {
    code?: unknown;
    message?: unknown;
    details?: unknown;
  };
};

function isObject(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

async function parseApiError(response: Response): Promise<ApiError> {
  const fallback: ApiError = {
    code: "INTERNAL_ERROR",
    message: "Unexpected API error.",
    details: {},
    status: response.status,
  };
  try {
    const parsed = (await response.json()) as ApiErrorEnvelope;
    if (
      parsed.error &&
      typeof parsed.error.code === "string" &&
      typeof parsed.error.message === "string"
    ) {
      return {
        code: parsed.error.code,
        message: parsed.error.message,
        details: isObject(parsed.error.details) ? parsed.error.details : {},
        status: response.status,
      };
    }
    return fallback;
  } catch {
    return fallback;
  }
}

export default function ReviewDetailPage() {
  const router = useRouter();
  const params = useParams<{ reviewId: string }>();
  const reviewId = params.reviewId;

  const [isLoading, setIsLoading] = useState(true);
  const [isRetrying, setIsRetrying] = useState(false);
  const [reviewDetail, setReviewDetail] = useState<ReviewDetailResponse | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function loadReview() {
      setIsLoading(true);
      const response = await fetch(`/api/bff/reviews/${reviewId}`, {
        method: "GET",
        cache: "no-store",
      });
      if (!response.ok) {
        const apiError = await parseApiError(response);
        if (!cancelled) {
          setError(apiError);
          setReviewDetail(null);
          setIsLoading(false);
        }
        return;
      }
      const payload = (await response.json()) as ReviewDetailResponse;
      if (!cancelled) {
        setError(null);
        setReviewDetail(payload);
        setIsLoading(false);
      }
    }
    void loadReview();
    return () => {
      cancelled = true;
    };
  }, [reviewId]);

  async function retryFailedReview() {
    const stored = getStoredReviewAttempt();
    if (!stored) {
      setStatusMessage("No saved draft found. Return to /app and submit again.");
      return;
    }

    setIsRetrying(true);
    setStatusMessage(null);
    try {
      const nextAttempt = await createNewReviewAttempt(stored.draft);
      const response = await fetch("/api/bff/reviews", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          call_id: stored.draft.call_id,
          node_id: stored.draft.node_id,
          snippet_text: stored.draft.snippet_text,
          idempotency_key: nextAttempt.idempotencyKey,
          payload_sha256: nextAttempt.payloadSha256,
          created_at_ms: nextAttempt.createdAtMs,
        }),
      });
      if (!response.ok) {
        const apiError = await parseApiError(response);
        if (apiError.code === "QUOTA_EXCEEDED") {
          setStatusMessage("Daily review limit reached. Try again after reset.");
          return;
        }
        if (apiError.code === "REVIEWS_DISABLED") {
          setStatusMessage("Reviews are temporarily disabled.");
          return;
        }
        setStatusMessage(apiError.message);
        return;
      }
      const payload = (await response.json()) as { review_id?: string };
      if (!payload.review_id) {
        setStatusMessage("Retry succeeded but no review id was returned.");
        return;
      }
      router.push(`/app/reviews/${payload.review_id}`);
    } catch (retryError) {
      setStatusMessage(
        retryError instanceof Error ? retryError.message : "Retry failed.",
      );
    } finally {
      setIsRetrying(false);
    }
  }

  if (isLoading) {
    return (
      <main className="mx-auto flex min-h-screen w-full max-w-5xl flex-col px-6 py-12 md:px-10">
        <div className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-8">
          <p className="text-sm text-[var(--color-muted-foreground)]">Loading review...</p>
        </div>
      </main>
    );
  }

  if (error) {
    if (error.code === "UNAUTHORIZED") {
      return (
        <main className="mx-auto flex min-h-screen w-full max-w-3xl flex-col items-start justify-center px-6 py-12">
          <h1 className="text-2xl font-semibold text-[var(--color-foreground)]">
            Sign in required
          </h1>
          <p className="mt-2 text-sm text-[var(--color-muted-foreground)]">
            Your session expired. Sign in again to view this review.
          </p>
          <Link
            className="mt-6 inline-flex h-11 items-center justify-center rounded-[var(--radius-md)] bg-[var(--color-primary)] px-5 text-sm font-medium text-white"
            href={`/sign-in?redirect_url=/app/reviews/${reviewId}`}
          >
            Continue to sign in
          </Link>
        </main>
      );
    }

    if (error.code === "REVIEW_NOT_FOUND") {
      return (
        <main className="mx-auto flex min-h-screen w-full max-w-3xl flex-col items-start justify-center px-6 py-12">
          <h1 className="text-2xl font-semibold text-[var(--color-foreground)]">
            Review not found
          </h1>
          <p className="mt-2 text-sm text-[var(--color-muted-foreground)]">
            This review does not exist or is not available for your account.
          </p>
          <Link
            className="mt-6 inline-flex h-11 items-center justify-center rounded-[var(--radius-md)] border border-[var(--color-border)] px-5 text-sm font-medium text-[var(--color-foreground)]"
            href="/app"
          >
            Back to submit
          </Link>
        </main>
      );
    }

    return (
      <main className="mx-auto flex min-h-screen w-full max-w-3xl flex-col items-start justify-center px-6 py-12">
        <h1 className="text-2xl font-semibold text-[var(--color-foreground)]">
          Unable to load review
        </h1>
        <p className="mt-2 text-sm text-red-600">{error.message}</p>
        <Link
          className="mt-6 inline-flex h-11 items-center justify-center rounded-[var(--radius-md)] border border-[var(--color-border)] px-5 text-sm font-medium text-[var(--color-foreground)]"
          href="/app"
        >
          Back to submit
        </Link>
      </main>
    );
  }

  if (!reviewDetail) {
    return null;
  }

  const isFailed = reviewDetail.review.status === "FAILED";
  const isPending = reviewDetail.review.status === "PENDING";

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-5xl flex-col gap-6 px-6 py-12 md:px-10">
      <header className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-8 shadow-sm">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--color-muted-foreground)]">
          Review
        </p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight text-[var(--color-foreground)]">
          {reviewDetail.review.status === "COMPLETED"
            ? "Feedback Ready"
            : reviewDetail.review.status === "FAILED"
              ? "Review Failed"
              : "Review In Progress"}
        </h1>
        <p className="mt-3 text-sm text-[var(--color-muted-foreground)]">
          Review ID: <span className="font-mono">{reviewDetail.review.id}</span>
        </p>

        {reviewDetail.review.overall_summary ? (
          <p className="mt-4 rounded-[var(--radius-md)] border border-[var(--color-border)] bg-white px-4 py-3 text-sm leading-6 text-[var(--color-foreground)]">
            {reviewDetail.review.overall_summary}
          </p>
        ) : null}

        {isPending ? (
          <p className="mt-4 text-sm text-[var(--color-muted-foreground)]">
            Still processing. Refresh this page in a few moments.
          </p>
        ) : null}

        {isFailed ? (
          <div className="mt-4 space-y-3">
            <p className="text-sm text-[var(--color-muted-foreground)]">
              Retry uses your previous draft with a new idempotency key.
            </p>
            <div className="flex flex-wrap gap-3">
              <button
                className="inline-flex h-11 items-center justify-center rounded-[var(--radius-md)] bg-[var(--color-primary)] px-5 text-sm font-medium text-white transition hover:brightness-105 disabled:cursor-not-allowed disabled:opacity-60"
                disabled={isRetrying}
                onClick={retryFailedReview}
                type="button"
              >
                {isRetrying ? "Retrying..." : "Retry Review"}
              </button>
              <Link
                className="inline-flex h-11 items-center justify-center rounded-[var(--radius-md)] border border-[var(--color-border)] px-5 text-sm font-medium text-[var(--color-foreground)]"
                href="/app"
              >
                Edit and resubmit
              </Link>
            </div>
            {statusMessage ? <p className="text-sm text-red-600">{statusMessage}</p> : null}
          </div>
        ) : null}
      </header>

      {reviewDetail.cards.length > 0 ? (
        <section className="grid gap-4">
          {reviewDetail.cards.map((card) => (
            <article
              className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-6 shadow-sm"
              key={card.id}
            >
              <div className="flex items-center justify-between gap-3">
                <p className="text-xs font-semibold uppercase tracking-[0.15em] text-[var(--color-muted-foreground)]">
                  Rating
                </p>
                <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
                  {card.rating}
                </span>
              </div>
              <p className="mt-3 text-sm leading-6 text-[var(--color-foreground)]">
                {card.feedback_text}
              </p>
            </article>
          ))}
        </section>
      ) : (
        <section className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-6 text-sm text-[var(--color-muted-foreground)]">
          No review cards available yet.
        </section>
      )}
    </main>
  );
}

