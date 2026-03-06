// frontend/src/app/app/reviews/[reviewId]/page.tsx
"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import {
  clearReviewAttempt,
  createNewReviewAttempt,
  getStoredReviewAttempt,
} from "@/lib/review-attempt";
import { APP_CREATE_REVIEW_ROUTE, APP_REVIEWS_ROUTE } from "@/lib/routes";
import type {
  ApiError,
  NodeSummary,
  ReviewDetailResponse,
} from "@/lib/bff/types";
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

type ReviewCardGroup = {
  key: string;
  title: string;
  nodeLogicalId: string | null;
  cards: ReviewDetailResponse["cards"];
};

type ReviewDetailViewState =
  | "call_linked"
  | "legacy_fallback"
  | "proof_path_unmapped";

type ReviewDetailViewModel = ReviewDetailResponse & {
  detail_state?: ReviewDetailViewState;
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

function buildSignInRedirectHref(path: string): string {
  const params = new URLSearchParams({ redirect_url: path });
  return `/sign-in?${params.toString()}`;
}

function sortCallNodes(nodes: NodeSummary[]): NodeSummary[] {
  return [...nodes].sort((left, right) => {
    if (left.order_index !== right.order_index) {
      return left.order_index - right.order_index;
    }
    const leftLogicalId = left.logical_id ?? "";
    const rightLogicalId = right.logical_id ?? "";
    return leftLogicalId.localeCompare(rightLogicalId);
  });
}

function buildOrderedCardGroups(
  reviewDetail: ReviewDetailResponse,
  sortedCallNodes: NodeSummary[],
): ReviewCardGroup[] {
  const groupsByKey = new Map<string, ReviewCardGroup>();
  reviewDetail.cards.forEach((card) => {
    const key = card.node_logical_id ?? `node:${card.node_title}`;
    const existing = groupsByKey.get(key);
    if (existing) {
      existing.cards.push(card);
      return;
    }
    groupsByKey.set(key, {
      key,
      title: card.node_title,
      nodeLogicalId: card.node_logical_id ?? null,
      cards: [card],
    });
  });

  const shouldUseCallOrdering =
    reviewDetail.ordering_source !== "review_payload_fallback" &&
    sortedCallNodes.length > 0;
  if (!shouldUseCallOrdering) {
    return Array.from(groupsByKey.values());
  }

  const nodeTitleByLogicalId = new Map<string, string>();
  const nodeIndexByLogicalId = new Map<string, number>();
  const nodeById = new Map(sortedCallNodes.map((node) => [node.id, node]));

  function buildPathLabel(node: NodeSummary): string {
    const titleChain: string[] = [node.title];
    let parentId = node.parent_node_id;
    while (parentId) {
      const parent = nodeById.get(parentId);
      if (!parent) {
        break;
      }
      titleChain.unshift(parent.title);
      parentId = parent.parent_node_id;
    }
    return titleChain.join(" / ");
  }

  sortedCallNodes.forEach((node, index) => {
    if (typeof node.logical_id !== "string") {
      return;
    }
    nodeTitleByLogicalId.set(node.logical_id, buildPathLabel(node));
    nodeIndexByLogicalId.set(node.logical_id, index);
  });

  const groups = Array.from(groupsByKey.values()).map((group) => {
    if (group.nodeLogicalId && nodeTitleByLogicalId.has(group.nodeLogicalId)) {
      return {
        ...group,
        title: nodeTitleByLogicalId.get(group.nodeLogicalId) ?? group.title,
      };
    }
    return group;
  });

  return groups.sort((left, right) => {
    const leftId = left.nodeLogicalId ?? "";
    const rightId = right.nodeLogicalId ?? "";
    const leftIndex =
      typeof left.nodeLogicalId === "string"
        ? nodeIndexByLogicalId.get(left.nodeLogicalId)
        : undefined;
    const rightIndex =
      typeof right.nodeLogicalId === "string"
        ? nodeIndexByLogicalId.get(right.nodeLogicalId)
        : undefined;
    const leftMapped = typeof leftIndex === "number";
    const rightMapped = typeof rightIndex === "number";
    if (leftMapped && rightMapped) {
      if (leftIndex !== rightIndex) {
        return leftIndex - rightIndex;
      }
      return leftId.localeCompare(rightId);
    }
    if (leftMapped) {
      return -1;
    }
    if (rightMapped) {
      return 1;
    }
    return leftId.localeCompare(rightId);
  });
}

function inferDetailState(
  reviewDetail: ReviewDetailViewModel,
): ReviewDetailViewState {
  if (reviewDetail.detail_state) {
    return reviewDetail.detail_state;
  }
  if (
    reviewDetail.ordering_source === "review_payload_fallback" ||
    reviewDetail.call_id == null
  ) {
    return "legacy_fallback";
  }
  if (
    reviewDetail.call_code === "erc_stg_2026_full" &&
    Array.isArray(reviewDetail.unmapped_node_logical_ids) &&
    reviewDetail.unmapped_node_logical_ids.length > 0
  ) {
    return "proof_path_unmapped";
  }
  return "call_linked";
}

export default function ReviewDetailPage() {
  const router = useRouter();
  const params = useParams<{ reviewId: string }>();
  const reviewId = params.reviewId;

  const [isLoading, setIsLoading] = useState(true);
  const [isRetrying, setIsRetrying] = useState(false);
  const [reviewDetail, setReviewDetail] = useState<ReviewDetailViewModel | null>(
    null,
  );
  const [callNodes, setCallNodes] = useState<NodeSummary[] | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [exportFeedback, setExportFeedback] = useState<ExportFeedback | null>(
    null,
  );
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteErrorMessage, setDeleteErrorMessage] = useState<string | null>(
    null,
  );
  const [hasPollingCapReached, setHasPollingCapReached] = useState(false);
  const [pollingNotice, setPollingNotice] = useState<string | null>(null);
  const reviewStatus = reviewDetail?.review.status;

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
          setCallNodes(null);
          setIsLoading(false);
        }
        return;
      }
      const payload = (await response.json()) as ReviewDetailViewModel;
      let nextCallNodes: NodeSummary[] | null = null;
      if (typeof payload.call_id === "string" && payload.call_id.length > 0) {
        const callNodesResponse = await fetch(`/api/bff/calls/${payload.call_id}/nodes`, {
          method: "GET",
          cache: "no-store",
        });
        if (callNodesResponse.ok) {
          const callNodesPayload = (await callNodesResponse.json()) as {
            nodes?: NodeSummary[];
          };
          nextCallNodes = Array.isArray(callNodesPayload.nodes)
            ? sortCallNodes(callNodesPayload.nodes)
            : [];
        }
      }
      if (!cancelled) {
        setError(null);
        setReviewDetail(payload);
        setCallNodes(nextCallNodes);
        setIsLoading(false);
      }
    }
    void loadReview();
    return () => {
      cancelled = true;
    };
  }, [reviewId]);

  useEffect(() => {
    if (!reviewStatus || !isPendingReview(reviewStatus)) {
      setHasPollingCapReached(false);
      setPollingNotice(null);
      return;
    }

    let cancelled = false;
    let stopped = false;
    let requestInFlight = false;
    const startedAtMs = Date.now();

    async function pollReviewStatus() {
      if (cancelled || stopped || requestInFlight) {
        return;
      }
      if (Date.now() - startedAtMs >= POLL_MAX_DURATION_MS) {
        setHasPollingCapReached(true);
        setPollingNotice(null);
        stopped = true;
        return;
      }

      requestInFlight = true;
      try {
        const response = await fetch(`/api/bff/reviews/${reviewId}`, {
          method: "GET",
          cache: "no-store",
        });
        if (!response.ok) {
          const apiError = await parseApiError(response);
          if (
            !cancelled &&
            (apiError.code === "UNAUTHORIZED" ||
              apiError.code === "REVIEW_NOT_FOUND")
          ) {
            setError(apiError);
            stopped = true;
            return;
          }
          if (!cancelled) {
            setPollingNotice(
              "Temporary issue checking status. Retrying automatically...",
            );
          }
          return;
        }

        const payload = (await response.json()) as ReviewDetailViewModel;
        if (cancelled) {
          return;
        }

        setReviewDetail(payload);
        setError(null);
        setPollingNotice(null);

        if (!isPendingReview(payload.review.status)) {
          stopped = true;
          setHasPollingCapReached(false);
        }
      } catch {
        if (!cancelled) {
          setPollingNotice(
            "Network issue while checking status. Retrying automatically...",
          );
        }
      } finally {
        requestInFlight = false;
      }
    }

    const intervalId = window.setInterval(() => {
      void pollReviewStatus();
    }, POLL_INTERVAL_MS);

    void pollReviewStatus();

    return () => {
      cancelled = true;
      stopped = true;
      window.clearInterval(intervalId);
    };
  }, [reviewId, reviewStatus]);

  async function retryFailedReview() {
    const stored = getStoredReviewAttempt();
    if (!stored) {
      setStatusMessage(
        "No saved draft found. Return to /app and submit again.",
      );
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
          review_stage: stored.draft.review_stage,
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
          setStatusMessage(
            "Daily review limit reached. Try again after reset.",
          );
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

  function handleStartNewReview() {
    clearReviewAttempt();
    router.push(APP_CREATE_REVIEW_ROUTE);
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
      router.push(APP_CREATE_REVIEW_ROUTE);
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
          <div aria-hidden="true" className="space-y-4">
            <div className="h-4 w-20 animate-pulse rounded bg-[var(--color-surface-muted)]" />
            <div className="h-8 w-60 animate-pulse rounded bg-[var(--color-surface-muted)]" />
            <div className="h-4 w-48 animate-pulse rounded bg-[var(--color-surface-muted)]" />
            <div className="h-24 w-full animate-pulse rounded-[var(--radius-md)] bg-[var(--color-surface-muted)]" />
          </div>
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
            href={buildSignInRedirectHref(`/app/reviews/${reviewId}`)}
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
  const hasOverallSummary = Boolean(
    reviewDetail.review.overall_summary?.trim(),
  );
  const submittedNodes = reviewDetail.submitted_leaf_ids ?? [];
  const sortedCallNodes = callNodes ?? [];
  const leafCallNodes = sortedCallNodes.filter((node) => node.has_expectations);
  const nodeById = new Map(sortedCallNodes.map((node) => [node.id, node]));
  const nodeByLogicalId = new Map(
    sortedCallNodes
      .filter((node) => typeof node.logical_id === "string")
      .map((node) => [node.logical_id as string, node]),
  );

  function buildPathLabel(node: NodeSummary): string {
    const titleChain: string[] = [node.title];
    let parentId = node.parent_node_id;
    while (parentId) {
      const parent = nodeById.get(parentId);
      if (!parent) {
        break;
      }
      titleChain.unshift(parent.title);
      parentId = parent.parent_node_id;
    }
    return titleChain.join(" / ");
  }

  const nodeTitleByLogicalId = new Map(
    leafCallNodes
      .filter((node) => typeof node.logical_id === "string")
      .map((node) => [node.logical_id as string, buildPathLabel(node)]),
  );
  const reviewedNodeLabels = [...submittedNodes]
    .sort((left, right) => {
      const leftNode = nodeByLogicalId.get(left);
      const rightNode = nodeByLogicalId.get(right);
      if (!leftNode || !rightNode) {
        return left.localeCompare(right);
      }
      if (leftNode.order_index !== rightNode.order_index) {
        return leftNode.order_index - rightNode.order_index;
      }
      return left.localeCompare(right);
    })
    .map((nodeId) => nodeTitleByLogicalId.get(nodeId) ?? nodeId);
  const submittedSet = new Set(submittedNodes);
  const notReviewedNodeLabels = leafCallNodes
    .filter(
      (node) =>
        typeof node.logical_id === "string" && !submittedSet.has(node.logical_id),
    )
    .map((node) => buildPathLabel(node));
  const orderedCardGroups = buildOrderedCardGroups(reviewDetail, sortedCallNodes);
  const detailState = inferDetailState(reviewDetail);
  const fallbackToPayloadOrder =
    detailState === "legacy_fallback" ||
    reviewDetail.call_id == null ||
    sortedCallNodes.length === 0;
  const hasCoverageSummary =
    submittedNodes.length > 0 || notReviewedNodeLabels.length > 0;

  const compatibilityLines = (reviewDetail.compatibility_notes ?? []).map((note) => {
    const nodeSuffix =
      note.node_logical_ids.length > 0
        ? ` [${note.node_logical_ids.join(", ")}]`
        : "";
    switch (note.note_type) {
      case "deprecated_container_submission":
        return `deprecated_container_submission: ${note.message}${nodeSuffix}`;
      case "moved_legacy_node_reference":
        return `moved_legacy_node_reference: ${note.message}${nodeSuffix}`;
      case "mixed_version_review":
        return `mixed_version_review: ${note.message}${nodeSuffix}`;
      default:
        return note.message;
    }
  });

  const hasCompatibilityNotes = compatibilityLines.length > 0;

  const reviewedSectionText =
    reviewedNodeLabels.length > 0 ? reviewedNodeLabels.join(", ") : "None";
  const notReviewedSectionText =
    notReviewedNodeLabels.length > 0 ? notReviewedNodeLabels.join(", ") : "None";

  return (
    <article
      className="mx-auto flex w-full max-w-5xl flex-col gap-6 px-6 py-12 md:px-10"
      aria-labelledby="review-title"
    >
      <header className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-8 shadow-sm">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--color-muted-foreground)]">
          Review
        </p>
        <h1
          id="review-title"
          className="mt-2 text-3xl font-semibold tracking-tight text-[var(--color-foreground)]"
        >
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

        {hasCoverageSummary ? (
          <div className="mt-4 rounded-[var(--radius-md)] border border-[var(--color-border)] bg-white px-4 py-3 text-sm text-[var(--color-foreground)]">
            <p className="font-medium">Coverage summary</p>
            <p className="mt-1">
              Reviewed sections: {reviewedSectionText}
            </p>
            <p className="mt-1 text-[var(--color-muted-foreground)]">
              Not reviewed sections: {notReviewedSectionText}
            </p>
          </div>
        ) : null}
        {hasCompatibilityNotes ? (
          <div className="mt-3 rounded-[var(--radius-md)] border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
            <p className="font-medium">Compatibility notes</p>
            <ul className="mt-1 list-disc pl-5">
              {compatibilityLines.map((line) => (
                <li key={line}>{line}</li>
              ))}
            </ul>
          </div>
        ) : null}
        {fallbackToPayloadOrder ? (
          <p className="mt-3 text-sm text-[var(--color-muted-foreground)]">
            Call metadata unavailable; using review payload order.
          </p>
        ) : null}
        {detailState === "proof_path_unmapped" ? (
          <p className="mt-3 text-sm text-amber-700">
            Some submitted proof-call sections could not be mapped to call metadata and are shown as unmapped.
          </p>
        ) : null}

        <nav aria-label="Review actions" className="mt-4 flex flex-wrap gap-3">
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
          <button
            className="inline-flex h-11 items-center justify-center rounded-[var(--radius-md)] border border-[var(--color-border)] bg-white px-5 text-sm font-medium text-[var(--color-foreground)]"
            onClick={handleStartNewReview}
            type="button"
          >
            Start new review
          </button>
          <Link
            className="inline-flex h-11 items-center justify-center rounded-[var(--radius-md)] border border-[var(--color-border)] px-5 text-sm font-medium text-[var(--color-foreground)]"
            href={APP_REVIEWS_ROUTE}
          >
            My reviews
          </Link>
        </nav>
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
          <div className="mt-4 space-y-2">
            <p className="text-sm text-[var(--color-muted-foreground)]">
              {hasPollingCapReached
                ? "Still processing after 90 seconds. This review may still finish soon; refresh to check again."
                : "Still processing. Checking status automatically every few seconds."}
            </p>
            <p className="text-sm text-[var(--color-muted-foreground)]">
              You can keep waiting, open My reviews, or start a new review.
            </p>
            {pollingNotice ? (
              <p className="text-sm text-[var(--color-muted-foreground)]">
                {pollingNotice}
              </p>
            ) : null}
          </div>
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
              <button
                className="inline-flex h-11 items-center justify-center rounded-[var(--radius-md)] border border-[var(--color-border)] px-5 text-sm font-medium text-[var(--color-foreground)]"
                onClick={handleStartNewReview}
                type="button"
              >
                Start new review
              </button>
            </div>
            {statusMessage ? (
              <p className="text-sm text-red-600">{statusMessage}</p>
            ) : null}
          </div>
        ) : null}
      </header>

      {reviewDetail.cards.length > 0 ? (
        <div
          role="region"
          aria-label="Review Feedback Cards"
          className="grid gap-4"
        >
          {orderedCardGroups.map((group) => (
            <section
              className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-4"
              key={group.key}
              aria-labelledby={`heading-group-${group.key}`}
            >
              <h2
                id={`heading-group-${group.key}`}
                className="text-base font-semibold text-[var(--color-foreground)]"
              >
                Reviewed section: {group.title}
              </h2>
                <div className="mt-3 grid gap-4">
                  {group.cards.map((card, index) => (
                    <ReviewCard
                      key={`${group.key}:${card.id}`}
                      index={index + 1}
                      criterion={card.criterion}
                      description={card.criterion_description}
                    evaluationElementName={card.evaluation_element_name}
                    expectationGuidanceNote={card.expectation_guidance_note}
                    rating={card.rating}
                    feedback={card.feedback_text}
                    assessmentStatus={card.assessment_status}
                    notAssessableReason={card.not_assessable_reason}
                  />
                ))}
              </div>
            </section>
          ))}
          {hasCoverageSummary
            ? notReviewedNodeLabels.map((nodeLabel) => (
                <section
                  className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-4"
                  key={`not-reviewed-${nodeLabel}`}
                  aria-labelledby={`heading-not-reviewed-${nodeLabel}`}
                >
                  <h2
                    id={`heading-not-reviewed-${nodeLabel}`}
                    className="text-base font-semibold text-[var(--color-foreground)]"
                  >
                    Not reviewed section: {nodeLabel}
                  </h2>
                  <div className="mt-3 rounded-xl border border-[var(--color-border)] bg-[var(--color-background)] px-5 py-4 text-sm text-[var(--color-muted-foreground)]">
                    No text was submitted for this section in this review, so no
                    evaluation cards were generated.
                  </div>
                </section>
              ))
            : null}
        </div>
      ) : (
        <section className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-6 text-sm text-[var(--color-muted-foreground)]">
          No review cards available yet.
        </section>
      )}
    </article>
  );
}
