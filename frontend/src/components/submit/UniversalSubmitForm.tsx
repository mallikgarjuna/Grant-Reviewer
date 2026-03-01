"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import type {
  ApiError,
  CallNodesMetadataResponse,
  CallSummary,
  ComplianceCheckResponse,
  NodeSummary,
  StructuredReviewNodeInput,
} from "@/lib/bff/types";
import { buildReviewDetailRoute, SIGN_IN_ROUTE } from "@/lib/routes";
import { clearDraft, loadDraft, saveDraft } from "@/lib/submit/draftStore";
import {
  loadStructuredCalls,
  type StructuredCallSummary,
} from "@/lib/submit/loadStructuredCalls";
import { buildRenderModel, type RenderModelResult } from "@/lib/submit/renderModel";
import { trackClientEvent } from "@/lib/telemetry/clientTelemetry";

type ApiErrorEnvelope = {
  error?: {
    code?: unknown;
    message?: unknown;
    details?: unknown;
  };
};

const DOMAIN_DRAFT_KEY = "__selected_domain";

function isRecord(value: unknown): value is Record<string, unknown> {
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
        details: isRecord(parsed.error.details) ? parsed.error.details : {},
        status: response.status,
      };
    }
  } catch {
    return fallback;
  }
  return fallback;
}

export function UniversalSubmitForm() {
  const router = useRouter();
  const [calls, setCalls] = useState<StructuredCallSummary[]>([]);
  const [isLoadingCalls, setIsLoadingCalls] = useState(true);
  const [callError, setCallError] = useState<string | null>(null);
  const [gatingWarning, setGatingWarning] = useState<string | null>(null);
  const [selectedCallId, setSelectedCallId] = useState("");
  const [nodes, setNodes] = useState<NodeSummary[]>([]);
  const [renderModel, setRenderModel] = useState<RenderModelResult>({
    state: "ready",
    nodes: [],
    metadataFallbackCount: 0,
  });
  const [draft, setDraft] = useState<Record<string, string>>({});
  const [selectedDomain, setSelectedDomain] = useState<string | null>(null);
  const [hardBlockErrors, setHardBlockErrors] = useState<string[]>([]);
  const [complianceWarnings, setComplianceWarnings] = useState<
    ComplianceCheckResponse["warnings"]
  >([]);
  const [formError, setFormError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function loadCalls() {
      setIsLoadingCalls(true);
      setCallError(null);
      try {
        const response = await fetch("/api/bff/calls", {
          method: "GET",
          cache: "no-store",
        });
        if (!response.ok) {
          throw new Error("calls failed");
        }
        const payload = (await response.json()) as { calls?: CallSummary[] };
        const allCalls = Array.isArray(payload.calls) ? payload.calls : [];
        const structuredResult = await loadStructuredCalls({ calls: allCalls });
        if (!cancelled) {
          setCalls(structuredResult.calls);
          setSelectedCallId(structuredResult.calls[0]?.id ?? "");
          trackClientEvent("universal_submit.gating_summary", {
            total_calls: allCalls.length,
            structured_calls: structuredResult.calls.length,
            warnings: structuredResult.warnings.length,
          });
          setGatingWarning(
            structuredResult.warnings.length > 0
              ? "Some calls were hidden due to config loading issues."
              : null,
          );
        }
      } catch {
        if (!cancelled) {
          setCallError("Unable to load funding calls.");
        }
      } finally {
        if (!cancelled) {
          setIsLoadingCalls(false);
        }
      }
    }

    void loadCalls();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!selectedCallId) {
      setNodes([]);
      return;
    }

    let cancelled = false;
    async function loadNodes() {
      if (!cancelled) {
        setCallError(null);
      }
      try {
        const selectedCall = calls.find((call) => call.id === selectedCallId) ?? null;
        const metadataCallCode = selectedCall?.code ?? "";

        const [nodesResult, metadataResult] = await Promise.allSettled([
          fetch(`/api/bff/calls/${selectedCallId}/nodes`, {
            method: "GET",
            cache: "no-store",
          }),
          metadataCallCode
            ? fetch(`/api/bff/calls/${encodeURIComponent(metadataCallCode)}/metadata`, {
                method: "GET",
                cache: "no-store",
              })
            : Promise.resolve(new Response(JSON.stringify({ nodes: [] }), { status: 200 })),
        ]);
        if (nodesResult.status !== "fulfilled" || !nodesResult.value.ok) {
          throw new Error("nodes failed");
        }
        const payload = (await nodesResult.value.json()) as { nodes?: NodeSummary[] };
        const metadataPayload =
          metadataResult.status === "fulfilled" && metadataResult.value.ok
            ? ((await metadataResult.value.json()) as CallNodesMetadataResponse)
            : null;
        const metadataByLogicalId =
          metadataPayload?.nodes?.reduce<Record<string, { title?: string | null }>>(
            (acc, node) => {
              acc[node.logical_id] = {
                title: node.title,
              };
              return acc;
            },
            {},
          ) ?? {};
        if (!cancelled) {
          const nextNodes = Array.isArray(payload.nodes) ? payload.nodes : [];
          const storedDraft = loadDraft(selectedCallId);
          const storedDomain = storedDraft[DOMAIN_DRAFT_KEY] ?? null;
          const nextRenderModel = buildRenderModel({
            nodes: nextNodes,
            metadataByLogicalId,
          });
          if (nextRenderModel.state !== "ready") {
            trackClientEvent("universal_submit.unsupported_call_selection", {
              reason: nextRenderModel.reason,
            });
          } else if (nextRenderModel.metadataFallbackCount > 0) {
            trackClientEvent("universal_submit.metadata_fallback_usage", {
              fallback_count: nextRenderModel.metadataFallbackCount,
            });
          }
          setNodes(nextNodes);
          setRenderModel(nextRenderModel);
          setSelectedDomain(storedDomain);
          setDraft((current) => {
            const next: Record<string, string> = {};
            if (nextRenderModel.state === "ready") {
              for (const node of nextRenderModel.nodes) {
                next[node.nodeLogicalId] =
                  storedDraft[node.nodeLogicalId] ?? current[node.nodeLogicalId] ?? "";
              }
            }
            return next;
          });
        }
      } catch {
        if (!cancelled) {
          setCallError("Unable to load funding call sections.");
        }
      }
    }

    void loadNodes();
    return () => {
      cancelled = true;
    };
  }, [calls, selectedCallId]);

  const selectedCall = calls.find((call) => call.id === selectedCallId) ?? null;
  const domainOptions = selectedCall?.domainOptions ?? [];
  const effectiveDomain =
    selectedDomain && domainOptions.some((option) => option.value === selectedDomain)
      ? selectedDomain
      : null;

  function serializeDraftState(
    nodeDraft: Record<string, string>,
    domain: string | null,
  ): Record<string, string> {
    if (!domain) {
      return { ...nodeDraft };
    }
    return {
      ...nodeDraft,
      [DOMAIN_DRAFT_KEY]: domain,
    };
  }

  useEffect(() => {
    setSelectedDomain((current) =>
      current && domainOptions.some((option) => option.value === current) ? current : null,
    );
  }, [domainOptions, selectedCallId]);

  function updateNodeDraft(nodeLogicalId: string, value: string) {
    if (!selectedCallId) {
      return;
    }
    setDraft((current) => {
      const next = {
        ...current,
        [nodeLogicalId]: value,
      };
      saveDraft(selectedCallId, serializeDraftState(next, effectiveDomain));
      return next;
    });
  }

  function buildNodesPayload(): StructuredReviewNodeInput[] {
    if (renderModel.state !== "ready") {
      return [];
    }
    return renderModel.nodes
      .map((node) => {
        return {
          node_logical_id: node.nodeLogicalId,
          text: draft[node.nodeLogicalId] ?? "",
        };
      })
      .filter((node) => node.text.trim().length > 0);
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError(null);
    setHardBlockErrors([]);
    setComplianceWarnings([]);
    if (!selectedCallId) {
      setFormError("Funding call is required before submission.");
      return;
    }

    await runComplianceThenMaybeSubmit();
  }

  async function submitStructuredReview(nonEmptyNodes: StructuredReviewNodeInput[]) {
    const response = await fetch("/api/bff/structured-review", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Idempotency-Key": crypto.randomUUID(),
      },
      body: JSON.stringify({
        review_stage: "STEP_1",
        call_id: selectedCallId,
        nodes: nonEmptyNodes,
      }),
    });
    if (!response.ok) {
      const apiError = await parseApiError(response);
      if (apiError.status === 401) {
        trackClientEvent("universal_submit.submit_outcome", { outcome: "auth_redirect" });
        router.push(SIGN_IN_ROUTE);
        return;
      }
      trackClientEvent("universal_submit.submit_outcome", { outcome: "api_error" });
      setFormError(apiError.message);
      return;
    }

    const payload = (await response.json()) as { review_id?: string };
    if (!payload.review_id) {
      trackClientEvent("universal_submit.submit_outcome", { outcome: "missing_review_id" });
      setFormError("Review submitted but no review id was returned.");
      return;
    }
    clearDraft(selectedCallId);
    const query = new URLSearchParams({
      submitted_nodes: nonEmptyNodes.map((node) => node.node_logical_id).join(","),
    });
    trackClientEvent("universal_submit.submit_outcome", { outcome: "success" });
    router.push(`${buildReviewDetailRoute(payload.review_id)}?${query.toString()}`);
  }

  async function runComplianceThenMaybeSubmit() {
    const nonEmptyNodes = buildNodesPayload();
    if (renderModel.state !== "ready") {
      setFormError("This call is currently unsupported for universal structured submit.");
      return;
    }
    if (nonEmptyNodes.length === 0) {
      setFormError("You must fill out at least one section before submitting.");
      return;
    }

    setIsSubmitting(true);
    try {
      const complianceResponse = await fetch("/api/bff/check-compliance", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          call_id: selectedCallId,
          domain: effectiveDomain,
          draft_nodes: renderModel.nodes.map((node) => ({
            node_logical_id: node.nodeLogicalId,
            text: draft[node.nodeLogicalId] ?? "",
          })),
        }),
      });
      if (!complianceResponse.ok) {
        const apiError = await parseApiError(complianceResponse);
        if (apiError.status === 422) {
          const detailNodeIds = Array.isArray(apiError.details.node_logical_ids)
            ? apiError.details.node_logical_ids.filter((item) => typeof item === "string")
            : [];
          setHardBlockErrors([apiError.message, ...detailNodeIds]);
          trackClientEvent("universal_submit.submit_outcome", {
            outcome: "compliance_hard_block",
          });
          return;
        }
        setFormError(apiError.message);
        trackClientEvent("universal_submit.submit_outcome", {
          outcome: "compliance_api_error",
        });
        return;
      }

      const compliance = (await complianceResponse.json()) as ComplianceCheckResponse;
      setComplianceWarnings(compliance.warnings);

      const blockingErrors = compliance.errors.filter((error) => error.is_blocking);
      if (blockingErrors.length > 0) {
        // Compliance errors can be duplicated across nodes (e.g., same word-limit rule);
        // prefix with node label for clarity and stable disambiguation.
        const labelByLogicalId = new Map(
          renderModel.nodes.map((node) => [node.nodeLogicalId, node.label] as const),
        );
        setHardBlockErrors(
          blockingErrors.map((error) => {
            const prefix =
              labelByLogicalId.get(error.node_logical_id) ?? error.node_logical_id;
            return `${prefix}: ${error.message}`;
          }),
        );
        return;
      }
      await submitStructuredReview(nonEmptyNodes);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-col px-6 py-12 md:px-10">
      <div className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-8 shadow-sm">
        <h1 className="text-3xl font-semibold tracking-tight text-[var(--color-foreground)]">
          Run a Grant Review
        </h1>
        <p className="mt-2 text-sm text-[var(--color-muted-foreground)]">
          Complete sections for evaluation criteria-grounded feedback.
        </p>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {gatingWarning ? (
            <div className="rounded-[var(--radius-md)] border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-900">
              {gatingWarning}
            </div>
          ) : null}
          <div className="space-y-2">
            <label
              className="text-sm font-medium text-[var(--color-foreground)]"
              htmlFor="call"
            >
              Funding Call
            </label>
            <select
              id="call"
              className="h-11 w-full rounded-[var(--radius-md)] border border-[var(--color-border)] bg-white px-3 text-sm"
              disabled={isLoadingCalls || calls.length === 0 || isSubmitting}
              onChange={(event) => setSelectedCallId(event.target.value)}
              value={selectedCallId}
            >
              {calls.map((call) => (
                <option key={call.id} value={call.id}>
                  {call.code} - {call.name}
                </option>
              ))}
            </select>
            {callError ? <p className="text-sm text-red-600">{callError}</p> : null}
          </div>

          {renderModel.state === "ready"
            ? renderModel.nodes.map((node) => {
                const logicalId = node.nodeLogicalId;
                const inputId = `node-${logicalId.replace(/_/g, "-")}`;
                return (
                  <div className="space-y-2" key={logicalId}>
                    <label
                      className="text-sm font-medium text-[var(--color-foreground)]"
                      htmlFor={inputId}
                    >
                      {node.label}
                    </label>
                    <textarea
                      id={inputId}
                      className="min-h-40 w-full rounded-[var(--radius-md)] border border-[var(--color-border)] bg-white p-3 text-sm leading-6"
                      onChange={(event) => updateNodeDraft(logicalId, event.target.value)}
                      value={draft[logicalId] ?? ""}
                    />
                  </div>
                );
              })
            : null}

          {domainOptions.length > 0 ? (
            <div className="space-y-2">
              <label
                className="text-sm font-medium text-[var(--color-foreground)]"
                htmlFor="domain"
              >
                Domain
              </label>
              <select
                id="domain"
                className="h-11 w-full rounded-[var(--radius-md)] border border-[var(--color-border)] bg-white px-3 text-sm"
                onChange={(event) => {
                  const nextDomain = event.target.value ? event.target.value : null;
                  setSelectedDomain(nextDomain);
                  if (selectedCallId) {
                    saveDraft(selectedCallId, serializeDraftState(draft, nextDomain));
                  }
                }}
                value={effectiveDomain ?? ""}
              >
                <option value="">No domain override</option>
                {domainOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          ) : null}

          {renderModel.state === "unsupported" ? (
            <div className="rounded-[var(--radius-md)] border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-900">
              {renderModel.message}
            </div>
          ) : null}
          {renderModel.state === "contract_error" ? (
            <div className="rounded-[var(--radius-md)] border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
              {renderModel.message}
            </div>
          ) : null}
          {hardBlockErrors.length > 0 ? (
            <div className="rounded-[var(--radius-md)] border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
              <p className="font-medium">Submission blocked</p>
              <ul className="mt-1 list-disc pl-5">
                {hardBlockErrors.map((line, index) => (
                  <li key={`${index}:${line}`}>{line}</li>
                ))}
              </ul>
            </div>
          ) : null}
          {complianceWarnings.length > 0 ? (
            <div className="rounded-[var(--radius-md)] border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-900">
              <p className="font-medium">Informational guidance (non-blocking)</p>
              <ul className="mt-1 list-disc pl-5">
                {complianceWarnings.map((warning) => (
                  <li key={`${warning.node_logical_id}:${warning.rule_id}`}>
                    {warning.message}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}

          {formError ? (
            <div className="rounded-[var(--radius-md)] border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
              {formError}
            </div>
          ) : null}

          <button
            className="inline-flex h-11 items-center justify-center rounded-[var(--radius-md)] bg-[var(--color-primary)] px-5 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-60"
            disabled={
              Boolean(callError) ||
              isLoadingCalls ||
              isSubmitting ||
              renderModel.state !== "ready"
            }
            type="submit"
          >
            {isSubmitting ? "Submitting..." : "Submit"}
          </button>
        </form>
      </div>
    </main>
  );
}
