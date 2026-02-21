"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import {
  MAX_SNIPPET_CHARS,
  getStoredReviewAttempt,
  getOrCreateReviewAttempt,
} from "@/lib/review-attempt";
import { resolveCallConfigUiState } from "@/lib/call-config";
import { APP_REVIEWS_ROUTE } from "@/lib/routes";
import type { ApiError, CallSummary, NodeSummary } from "@/lib/bff/types";

const SLOW_REQUEST_HINT_MS = 40_000;

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

export default function AppSubmitPage() {
  const router = useRouter();
  const [calls, setCalls] = useState<CallSummary[]>([]);
  const [nodes, setNodes] = useState<NodeSummary[]>([]);
  const [selectedCallId, setSelectedCallId] = useState("");
  const [selectedNodeId, setSelectedNodeId] = useState("");
  const [snippetText, setSnippetText] = useState("");
  const [isLoadingCalls, setIsLoadingCalls] = useState(true);
  const [isLoadingNodes, setIsLoadingNodes] = useState(false);
  const [isLoadingConfig, setIsLoadingConfig] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showSlowHint, setShowSlowHint] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [uiMode, setUiMode] = useState<"legacy_single_snippet" | "structured_nodes">(
    "legacy_single_snippet",
  );
  const [configWarning, setConfigWarning] = useState<string | null>(null);
  const [isCallNotFound, setIsCallNotFound] = useState(false);

  const snippetCount = useMemo(() => snippetText.length, [snippetText]);
  const selectedCall = useMemo(
    () => calls.find((call) => call.id === selectedCallId) ?? null,
    [calls, selectedCallId],
  );

  useEffect(() => {
    const stored = getStoredReviewAttempt();
    if (!stored) {
      return;
    }
    setSelectedCallId(stored.draft.call_id);
    setSelectedNodeId(stored.draft.node_id);
    setSnippetText(stored.draft.snippet_text);
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function loadCalls() {
      setIsLoadingCalls(true);
      const response = await fetch("/api/bff/calls", {
        method: "GET",
        cache: "no-store",
      });
      if (!response.ok) {
        const apiError = await parseApiError(response);
        if (!cancelled) {
          setFormError(apiError.message);
          setIsLoadingCalls(false);
        }
        return;
      }
      const payload = (await response.json()) as { calls?: CallSummary[] };
      if (!cancelled) {
        setCalls(Array.isArray(payload.calls) ? payload.calls : []);
        setIsLoadingCalls(false);
      }
    }
    void loadCalls();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    const activeCallCode = selectedCall?.code;
    if (!activeCallCode) {
      setUiMode("legacy_single_snippet");
      setConfigWarning(null);
      setIsCallNotFound(false);
      setIsLoadingConfig(false);
      setNodes([]);
      setSelectedNodeId("");
      return;
    }
    const resolvedCallCode = activeCallCode;

    let cancelled = false;
    async function loadCallConfig() {
      setIsLoadingConfig(true);
      const pathCallCode = encodeURIComponent(resolvedCallCode);
      let state = resolveCallConfigUiState({ kind: "network_error" });
      try {
        const response = await fetch(`/api/bff/calls/${pathCallCode}/config`, {
          method: "GET",
          cache: "no-store",
        });
        if (!response.ok) {
          state = resolveCallConfigUiState({
            kind: "http_error",
            status: response.status,
          });
        } else {
          const payload = (await response.json()) as unknown;
          state = resolveCallConfigUiState({
            kind: "success",
            status: 200,
            payload,
          });
        }
      } catch {
        state = resolveCallConfigUiState({ kind: "network_error" });
      }
      if (!cancelled) {
        setUiMode(state.uiMode);
        setConfigWarning(state.warningMessage);
        setIsCallNotFound(state.callNotFound);
        setIsLoadingConfig(false);
        if (state.uiMode !== "legacy_single_snippet" || state.callNotFound) {
          setNodes([]);
          setSelectedNodeId("");
        }
      }
    }
    void loadCallConfig();
    return () => {
      cancelled = true;
    };
  }, [selectedCall]);

  useEffect(() => {
    if (!selectedCallId || !selectedCall) {
      setNodes([]);
      setSelectedNodeId("");
      return;
    }
    if (uiMode !== "legacy_single_snippet" || isCallNotFound || isLoadingConfig) {
      setNodes([]);
      setSelectedNodeId("");
      setIsLoadingNodes(false);
      return;
    }

    let cancelled = false;
    async function loadNodes() {
      setIsLoadingNodes(true);
      const response = await fetch(`/api/bff/calls/${selectedCallId}/nodes`, {
        method: "GET",
        cache: "no-store",
      });
      if (!response.ok) {
        const apiError = await parseApiError(response);
        if (!cancelled) {
          setFormError(apiError.message);
          setNodes([]);
          setSelectedNodeId("");
          setIsLoadingNodes(false);
        }
        return;
      }
      const payload = (await response.json()) as { nodes?: NodeSummary[] };
      if (!cancelled) {
        const reviewableNodes = Array.isArray(payload.nodes)
          ? payload.nodes.filter((node) => node.has_expectations)
          : [];
        setNodes(reviewableNodes);
        setSelectedNodeId((current) =>
          reviewableNodes.some((node) => node.id === current)
            ? current
            : reviewableNodes[0]?.id ?? "",
        );
        setIsLoadingNodes(false);
      }
    }
    void loadNodes();
    return () => {
      cancelled = true;
    };
  }, [isCallNotFound, isLoadingConfig, selectedCall, selectedCallId, uiMode]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError(null);
    setFieldErrors({});

    const nextFieldErrors: Record<string, string> = {};
    if (!selectedCallId) {
      nextFieldErrors.call = "Select a funding call.";
    }
    if (!selectedNodeId) {
      nextFieldErrors.node = "Select a proposal section.";
    }
    if (!snippetText.trim()) {
      nextFieldErrors.snippet = "Paste a proposal snippet.";
    }
    if (snippetCount > MAX_SNIPPET_CHARS) {
      nextFieldErrors.snippet = `Snippet must be at most ${MAX_SNIPPET_CHARS} characters.`;
    }

    if (Object.keys(nextFieldErrors).length > 0) {
      setFieldErrors(nextFieldErrors);
      return;
    }

    setIsSubmitting(true);
    setShowSlowHint(false);

    const slowHintTimer = window.setTimeout(() => {
      setShowSlowHint(true);
    }, SLOW_REQUEST_HINT_MS);

    try {
      const attempt = await getOrCreateReviewAttempt({
        call_id: selectedCallId,
        node_id: selectedNodeId,
        snippet_text: snippetText,
      });

      const response = await fetch("/api/bff/reviews", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          call_id: selectedCallId,
          node_id: selectedNodeId,
          snippet_text: snippetText,
          idempotency_key: attempt.idempotencyKey,
          payload_sha256: attempt.payloadSha256,
          created_at_ms: attempt.createdAtMs,
        }),
      });

      if (!response.ok) {
        const apiError = await parseApiError(response);
        if (apiError.code === "SNIPPET_TOO_LONG") {
          setFieldErrors((current) => ({
            ...current,
            snippet:
              typeof apiError.details.max_chars === "number"
                ? `Snippet must be at most ${apiError.details.max_chars} characters.`
                : apiError.message,
          }));
        } else if (
          apiError.code === "CALL_NOT_FOUND" ||
          apiError.code === "NODE_NOT_FOUND" ||
          apiError.code === "NO_EXPECTATIONS" ||
          apiError.code === "NODE_NOT_IN_CALL" ||
          apiError.code === "VALIDATION_ERROR"
        ) {
          setFormError(apiError.message);
        } else if (apiError.code === "QUOTA_EXCEEDED") {
          setFormError("Daily review limit reached. Try again after reset.");
        } else if (apiError.code === "REVIEWS_DISABLED") {
          setFormError("Reviews are temporarily disabled. Please try again later.");
        } else {
          setFormError(apiError.message);
        }
        return;
      }

      const payload = (await response.json()) as { review_id?: string };
      if (!payload.review_id) {
        setFormError("Review was created but no review id was returned.");
        return;
      }
      router.push(`/app/reviews/${payload.review_id}`);
    } catch (error) {
      setFormError(error instanceof Error ? error.message : "Request failed.");
    } finally {
      window.clearTimeout(slowHintTimer);
      setIsSubmitting(false);
    }
  }

  if (isLoadingCalls) {
    return (
      <main className="mx-auto flex w-full max-w-5xl flex-col px-6 py-12 md:px-10">
        <div className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-8 shadow-sm">
          <div className="h-8 w-64 animate-pulse rounded bg-[var(--color-surface-muted)]" />
          <div className="mt-3 h-4 w-full max-w-xl animate-pulse rounded bg-[var(--color-surface-muted)]" />
          <div className="mt-8 space-y-6">
            <div className="space-y-2">
              <div className="h-4 w-28 animate-pulse rounded bg-[var(--color-surface-muted)]" />
              <div className="h-11 w-full animate-pulse rounded-[var(--radius-md)] bg-[var(--color-surface-muted)]" />
            </div>
            <div className="space-y-2">
              <div className="h-4 w-32 animate-pulse rounded bg-[var(--color-surface-muted)]" />
              <div className="h-11 w-full animate-pulse rounded-[var(--radius-md)] bg-[var(--color-surface-muted)]" />
            </div>
            <div className="space-y-2">
              <div className="h-4 w-32 animate-pulse rounded bg-[var(--color-surface-muted)]" />
              <div className="h-48 w-full animate-pulse rounded-[var(--radius-md)] bg-[var(--color-surface-muted)]" />
            </div>
          </div>
        </div>
      </main>
    );
  }

  if (!formError && calls.length === 0) {
    return (
      <main className="mx-auto flex w-full max-w-5xl flex-col px-6 py-12 md:px-10">
        <div className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-8 shadow-sm">
          <h1 className="text-3xl font-semibold tracking-tight text-[var(--color-foreground)]">
            Run a Grant Review
          </h1>
          <p className="mt-2 text-sm text-[var(--color-muted-foreground)]">
            We could not find any funding calls to review right now.
          </p>
          <div className="mt-6 rounded-[var(--radius-lg)] border border-dashed border-[var(--color-border)] bg-[var(--color-background)] px-5 py-6">
            <p className="text-sm text-[var(--color-foreground)]">
              Next step: refresh this page to retry loading calls, or open your existing reviews.
            </p>
            <div className="mt-4 flex flex-wrap gap-3">
              <button
                className="inline-flex h-10 items-center justify-center rounded-[var(--radius-md)] bg-[var(--color-primary)] px-4 text-sm font-medium text-[var(--color-primary-foreground)] transition hover:opacity-90"
                onClick={() => window.location.reload()}
                type="button"
              >
                Retry loading calls
              </button>
              <Link
                className="inline-flex h-10 items-center justify-center rounded-[var(--radius-md)] border border-[var(--color-border)] px-4 text-sm font-medium text-[var(--color-foreground)]"
                href={APP_REVIEWS_ROUTE}
              >
                Go to My Reviews
              </Link>
            </div>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-col px-6 py-12 md:px-10">
      <div className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-8 shadow-sm">
        <h1 className="text-3xl font-semibold tracking-tight text-[var(--color-foreground)]">
          Run a Grant Review
        </h1>
        <p className="mt-2 text-sm text-[var(--color-muted-foreground)]">
          Choose the call and proposal section, then submit a snippet for evaluation-criteria-grounded feedback.
        </p>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-2">
            <label className="text-sm font-medium text-[var(--color-foreground)]" htmlFor="call">
              Funding Call
            </label>
            <select
              id="call"
              className="h-11 w-full rounded-[var(--radius-md)] border border-[var(--color-border)] bg-white px-3 text-sm outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-primary)]"
              disabled={isLoadingCalls || isSubmitting}
              onChange={(event) => setSelectedCallId(event.target.value)}
              value={selectedCallId}
            >
              <option value="">Select a funding call</option>
              {calls.map((call) => (
                <option key={call.id} value={call.id}>
                  {call.code} - {call.name}
                </option>
              ))}
            </select>
            {fieldErrors.call ? (
              <p className="text-sm text-red-600">{fieldErrors.call}</p>
            ) : null}
            {isLoadingConfig ? (
              <p className="text-sm text-[var(--color-muted-foreground)]">
                Loading call configuration...
              </p>
            ) : null}
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-[var(--color-foreground)]" htmlFor="node">
              Proposal Section
            </label>
            <select
              id="node"
              className="h-11 w-full rounded-[var(--radius-md)] border border-[var(--color-border)] bg-white px-3 text-sm outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-primary)]"
              disabled={
                !selectedCallId ||
                isLoadingNodes ||
                isSubmitting ||
                isLoadingConfig ||
                uiMode !== "legacy_single_snippet" ||
                isCallNotFound
              }
              onChange={(event) => setSelectedNodeId(event.target.value)}
              value={selectedNodeId}
            >
              <option value="">Select a section</option>
              {nodes.map((node) => (
                <option key={node.id} value={node.id}>
                  {node.title}
                </option>
              ))}
            </select>
            {isLoadingNodes ? (
              <div aria-hidden="true" className="space-y-2 pt-1">
                <div className="h-3 w-40 animate-pulse rounded bg-[var(--color-surface-muted)]" />
                <div className="h-3 w-52 animate-pulse rounded bg-[var(--color-surface-muted)]" />
              </div>
            ) : null}
            {fieldErrors.node ? (
              <p className="text-sm text-red-600">{fieldErrors.node}</p>
            ) : null}
          </div>

          {uiMode === "structured_nodes" ? (
            <div className="rounded-[var(--radius-md)] border border-[var(--color-border)] bg-[var(--color-background)] px-3 py-3 text-sm text-[var(--color-foreground)]">
              Structured submissions are coming soon for this call. Please switch to a call using the legacy single-snippet mode for now.
            </div>
          ) : null}

          <div className="space-y-2">
            <label
              className="text-sm font-medium text-[var(--color-foreground)]"
              htmlFor="snippet-text"
            >
              Proposal Snippet
            </label>
            <textarea
              id="snippet-text"
              className="min-h-48 w-full rounded-[var(--radius-md)] border border-[var(--color-border)] bg-white p-3 text-sm leading-6 outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-primary)]"
              disabled={isSubmitting || uiMode !== "legacy_single_snippet" || isCallNotFound}
              onChange={(event) => setSnippetText(event.target.value)}
              placeholder="Paste the grant section text you want reviewed..."
              value={snippetText}
            />
            <p
              className={`text-sm ${
                snippetCount > MAX_SNIPPET_CHARS ? "text-red-600" : "text-[var(--color-muted-foreground)]"
              }`}
            >
              {snippetCount.toLocaleString()} / {MAX_SNIPPET_CHARS.toLocaleString()} characters
            </p>
            {fieldErrors.snippet ? (
              <p className="text-sm text-red-600">{fieldErrors.snippet}</p>
            ) : null}
          </div>

          {configWarning ? (
            <div className="rounded-[var(--radius-md)] border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-900">
              {configWarning}
            </div>
          ) : null}

          {isCallNotFound ? (
            <div className="rounded-[var(--radius-md)] border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
              The selected funding call configuration was not found. Submission is disabled for this call.
            </div>
          ) : null}

          {formError ? (
            <div className="rounded-[var(--radius-md)] border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
              {formError}
            </div>
          ) : null}

          {showSlowHint ? (
            <div className="rounded-[var(--radius-md)] border border-[var(--color-border)] bg-[var(--color-background)] px-3 py-3 text-sm text-[var(--color-muted-foreground)]">
              <p>This is taking longer than usual.</p>
              <p className="mt-1">Next steps:</p>
              <ul className="mt-1 list-disc space-y-1 pl-5">
                <li>Keep this tab open while your review request finishes.</li>
                <li>
                  Open{" "}
                  <Link
                    className="font-medium text-[var(--color-foreground)] underline underline-offset-2"
                    href={APP_REVIEWS_ROUTE}
                  >
                    My Reviews
                  </Link>{" "}
                  to check status updates.
                </li>
              </ul>
            </div>
          ) : null}

          <button
            className="inline-flex h-11 items-center justify-center rounded-[var(--radius-md)] bg-[var(--color-primary)] px-5 text-sm font-medium text-white transition hover:brightness-105 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={
              isSubmitting ||
              isLoadingCalls ||
              isLoadingConfig ||
              uiMode !== "legacy_single_snippet" ||
              isCallNotFound
            }
            type="submit"
          >
            {isSubmitting ? "Submitting..." : "Generate Review"}
          </button>
        </form>
      </div>
    </main>
  );
}
