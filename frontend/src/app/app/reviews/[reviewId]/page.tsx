"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import {
  clearReviewAttempt,
  createNewReviewAttempt,
  getStoredReviewAttempt,
} from "@/lib/review-attempt";
import type { ApiError, ReviewDetailResponse } from "@/lib/bff/types";
import { ReviewCard } from "@/components/review/ReviewCard";
import { ReviewSummary } from "@/components/review/ReviewSummary";

const POLL_INTERVAL_MS = 3_000;
const POLL_MAX_DURATION_MS = 90_000;

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

type ExportFeedback = {
  kind: "success" | "error";
  message: string;
};

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

function buildReviewExportText(reviewDetail: ReviewDetailResponse): string {
  const lines: string[] = [
    "PeerLens review export",
    "",
    `Review ID: ${reviewDetail.review.id}`,
    `Status: ${reviewDetail.review.status}`,
    "",
    "Summary:",
    reviewDetail.review.overall_summary ?? "No overall summary available.",
    "",
    "Cards:",
  ];

  if (reviewDetail.cards.length === 0) {
    lines.push("No review cards available.");
  } else {
    reviewDetail.cards.forEach((card, index) => {
      lines.push("");
      lines.push(`${index + 1}. Criterion: ${card.criterion}`);
      lines.push(`   Rating: ${card.rating}`);
      lines.push(`   Feedback: ${card.feedback_text}`);
    });
  }

  return lines.join("\n");
}

async function copyTextWithFallback(text: string): Promise<void> {
  if (navigator.clipboard?.writeText && window.isSecureContext) {
    await navigator.clipboard.writeText(text);
    return;
  }

  const textArea = document.createElement("textarea");
  textArea.value = text;
  textArea.setAttribute("readonly", "true");
  textArea.style.position = "fixed";
  textArea.style.left = "-9999px";
  textArea.style.top = "0";
  document.body.append(textArea);
  textArea.select();
  const copied = document.execCommand("copy");
  textArea.remove();

  if (!copied) {
    throw new Error("Clipboard write failed.");
  }
}

function isPendingReview(status: string): boolean {
  return status === "PENDING";
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
  const [exportFeedback, setExportFeedback] = useState<ExportFeedback | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteErrorMessage, setDeleteErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function loadReview() {
      setIsLoading(true);
      setExportFeedback(null);
      setDeleteErrorMessage(null);
      setShowDeleteConfirm(false);
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

  async function copyReviewAsText() {
    if (!reviewDetail) {
      return;
    }
    try {
      await copyTextWithFallback(buildReviewExportText(reviewDetail));
      setExportFeedback({
        kind: "success",
        message: "Copied review text to clipboard.",
      });
    } catch {
      setExportFeedback({
        kind: "error",
        message: "Unable to copy automatically. Use Download .txt instead.",
      });
    }
  }

  function downloadReviewAsText() {
    if (!reviewDetail) {
      return;
    }
    const payload = buildReviewExportText(reviewDetail);
    const blob = new Blob([payload], { type: "text/plain;charset=utf-8" });
    const objectUrl = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = objectUrl;
    anchor.download = `peerlens-review-${reviewDetail.review.id}.txt`;
    document.body.append(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(objectUrl);
    setExportFeedback({
      kind: "success",
      message: "Downloaded review as .txt.",
    });
  }

  async function deleteReviewAndRedirect() {
    setIsDeleting(true);
    setDeleteErrorMessage(null);
    try {
      const response = await fetch(`/api/bff/reviews/${reviewId}`, {
        method: "DELETE",
      });
      if (!response.ok) {
        const apiError = await parseApiError(response);
        if (apiError.code === "REVIEW_NOT_FOUND") {
          setDeleteErrorMessage("Review no longer exists or is unavailable.");
          return;
        }
        setDeleteErrorMessage("Unable to delete this review right now.");
        return;
      }
      clearReviewAttempt();
      router.push("/app");
    } catch {
      setDeleteErrorMessage("Unable to delete this review right now.");
    } finally {
      setIsDeleting(false);
    }
  }

  if (isLoading) {
    return (
      <main className="mx-auto flex w-full max-w-5xl flex-col px-6 py-12 md:px-10">
        <div className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-8">
          <p className="text-sm text-[var(--color-muted-foreground)]">Loading review...</p>
        </div>
      </main>
    );
  }

  if (error) {
    if (error.code === "UNAUTHORIZED") {
      return (
        <main className="mx-auto flex w-full max-w-3xl flex-col items-start justify-center px-6 py-12">
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
        <main className="mx-auto flex w-full max-w-3xl flex-col items-start justify-center px-6 py-12">
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
      <main className="mx-auto flex w-full max-w-3xl flex-col items-start justify-center px-6 py-12">
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
  const isPending = isPendingReview(reviewDetail.review.status);
  const hasOverallSummary = Boolean(reviewDetail.review.overall_summary?.trim());

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-col gap-6 px-6 py-12 md:px-10">
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

        {hasOverallSummary ? (
          <div className="mt-6">
            <ReviewSummary
              summary={{
                id: reviewDetail.review.id,
                status: reviewDetail.review.status,
                overall_rating: reviewDetail.review.overall_rating,
                overall_summary: reviewDetail.review.overall_summary,
              }}
            />
          </div>
        ) : null}

        <div className="mt-4 flex flex-wrap gap-3">
          <button
            className="inline-flex h-11 items-center justify-center rounded-[var(--radius-md)] bg-[var(--color-primary)] px-5 text-sm font-medium text-white transition hover:brightness-105"
            onClick={copyReviewAsText}
            type="button"
          >
            Copy as text
          </button>
          <button
            className="inline-flex h-11 items-center justify-center rounded-[var(--radius-md)] border border-[var(--color-border)] bg-white px-5 text-sm font-medium text-[var(--color-foreground)]"
            onClick={downloadReviewAsText}
            type="button"
          >
            Download .txt
          </button>
        </div>
        {exportFeedback ? (
          <p
            className={`mt-3 text-sm ${
              exportFeedback.kind === "error"
                ? "text-red-600"
                : "text-[var(--color-muted-foreground)]"
            }`}
          >
            {exportFeedback.message}
          </p>
        ) : null}
        <div className="mt-5 rounded-[var(--radius-md)] border border-[var(--color-border)] bg-white px-4 py-4">
          <p className="text-xs font-semibold uppercase tracking-[0.15em] text-[var(--color-muted-foreground)]">
            Data controls
          </p>
          <p className="mt-2 text-sm text-[var(--color-muted-foreground)]">
            Delete this review and its snippet data from your account.
          </p>
          {!showDeleteConfirm ? (
            <button
              className="mt-3 inline-flex h-11 items-center justify-center rounded-[var(--radius-md)] border border-red-300 bg-red-50 px-5 text-sm font-medium text-red-700 hover:bg-red-100"
              onClick={() => setShowDeleteConfirm(true)}
              type="button"
            >
              Delete review
            </button>
          ) : (
            <div className="mt-3 flex flex-wrap items-center gap-3">
              <button
                className="inline-flex h-11 items-center justify-center rounded-[var(--radius-md)] bg-red-600 px-5 text-sm font-medium text-white hover:brightness-105 disabled:cursor-not-allowed disabled:opacity-60"
                disabled={isDeleting}
                onClick={deleteReviewAndRedirect}
                type="button"
              >
                {isDeleting ? "Deleting..." : "Confirm delete"}
              </button>
              <button
                className="inline-flex h-11 items-center justify-center rounded-[var(--radius-md)] border border-[var(--color-border)] bg-white px-5 text-sm font-medium text-[var(--color-foreground)]"
                disabled={isDeleting}
                onClick={() => {
                  setShowDeleteConfirm(false);
                  setDeleteErrorMessage(null);
                }}
                type="button"
              >
                Cancel
              </button>
            </div>
          )}
          {deleteErrorMessage ? (
            <p className="mt-3 text-sm text-red-600">{deleteErrorMessage}</p>
          ) : null}
        </div>

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
            <ReviewCard
              key={card.id}
              criterion={card.criterion}
              description={card.criterion_description}
              rating={card.rating}
              feedback={card.feedback_text}
            />
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
