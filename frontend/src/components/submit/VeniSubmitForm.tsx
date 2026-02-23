"use client";

import { useEffect, useMemo, useState } from "react";

import { useLocalStorageDraft } from "@/hooks/useLocalStorageDraft";
import type { CallSummary } from "@/lib/bff/types";

const VENI_CALL_CODE = "nwo_veni_2025_preproposal";

type VeniDraft = {
  academic_profile: string;
  key_outputs: string;
  research_idea: string;
  domain: string | null;
};

const INITIAL_DRAFT: VeniDraft = {
  academic_profile: "",
  key_outputs: "",
  research_idea: "",
  domain: null,
};

function countWords(text: string): number {
  const normalized = text.trim();
  if (!normalized) {
    return 0;
  }
  return normalized.split(/\s+/).length;
}

export function VeniSubmitForm() {
  const [calls, setCalls] = useState<CallSummary[]>([]);
  const [isLoadingCalls, setIsLoadingCalls] = useState(true);
  const [callError, setCallError] = useState<string | null>(null);
  const [selectedCallId, setSelectedCallId] = useState("");

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
          setCallError("Unable to load funding calls.");
          setIsLoadingCalls(false);
          return;
        }

        const payload = (await response.json()) as { calls?: CallSummary[] };
        const allCalls = Array.isArray(payload.calls) ? payload.calls : [];
        const veniCalls = allCalls.filter((item) => item.code === VENI_CALL_CODE);

        if (!cancelled) {
          setCalls(veniCalls);
          setSelectedCallId(veniCalls[0]?.id ?? "");
          if (veniCalls.length === 0) {
            setCallError("NWO Veni 2025 call is not available.");
          }
          setIsLoadingCalls(false);
        }
      } catch {
        if (!cancelled) {
          setCallError("Unable to load funding calls.");
          setIsLoadingCalls(false);
        }
      }
    }

    void loadCalls();

    return () => {
      cancelled = true;
    };
  }, []);

  const storageKey = "draft_nwo_veni_2025_preproposal_v1";

  const { value: draft, setValue: setDraft } = useLocalStorageDraft<VeniDraft>(
    storageKey,
    INITIAL_DRAFT,
  );

  const counters = useMemo(
    () => ({
      academic_profile: countWords(draft.academic_profile),
      key_outputs: countWords(draft.key_outputs),
      research_idea: countWords(draft.research_idea),
    }),
    [draft.academic_profile, draft.key_outputs, draft.research_idea],
  );

  const researchIdeaLimit = draft.domain === "science_enw" ? 500 : 100;

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-col px-6 py-12 md:px-10">
      <div className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-8 shadow-sm">
        <h1 className="text-3xl font-semibold tracking-tight text-[var(--color-foreground)]">
          Run a Grant Review
        </h1>
        <p className="mt-2 text-sm text-[var(--color-muted-foreground)]">
          Complete the NWO Veni 2025 preproposal sections for evaluation criteria-grounded
          feedback.
        </p>

        <p className="mt-4 rounded-[var(--radius-md)] border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-900">
          Please paste plain text. Complex formatting such as tables and images is not supported in
          this MVP.
        </p>

        <form className="mt-8 space-y-6" onSubmit={(event) => event.preventDefault()}>
          <div className="space-y-2">
            <label className="text-sm font-medium text-[var(--color-foreground)]" htmlFor="call">
              Funding Call
            </label>
            <select
              id="call"
              className="h-11 w-full rounded-[var(--radius-md)] border border-[var(--color-border)] bg-white px-3 text-sm outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-primary)]"
              disabled={isLoadingCalls || calls.length === 0}
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

          <div className="space-y-2">
            <label
              className="text-sm font-medium text-[var(--color-foreground)]"
              htmlFor="academic-profile"
            >
              Academic Profile
            </label>
            <textarea
              id="academic-profile"
              className="min-h-40 w-full rounded-[var(--radius-md)] border border-[var(--color-border)] bg-white p-3 text-sm leading-6 outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-primary)]"
              onChange={(event) =>
                setDraft((current) => ({ ...current, academic_profile: event.target.value }))
              }
              value={draft.academic_profile}
            />
            <p className="text-sm text-[var(--color-muted-foreground)]">
              {counters.academic_profile.toLocaleString()} words
            </p>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-[var(--color-foreground)]" htmlFor="key-outputs">
              Key Outputs
            </label>
            <textarea
              id="key-outputs"
              className="min-h-40 w-full rounded-[var(--radius-md)] border border-[var(--color-border)] bg-white p-3 text-sm leading-6 outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-primary)]"
              onChange={(event) =>
                setDraft((current) => ({ ...current, key_outputs: event.target.value }))
              }
              value={draft.key_outputs}
            />
            <p className="text-sm text-[var(--color-muted-foreground)]">
              {counters.key_outputs.toLocaleString()} words
            </p>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-[var(--color-foreground)]" htmlFor="science-enw">
              ENW/Science Pilot
            </label>
            <div className="flex items-center gap-2">
              <input
                checked={draft.domain === "science_enw"}
                id="science-enw"
                onChange={(event) =>
                  setDraft((current) => ({
                    ...current,
                    domain: event.target.checked ? "science_enw" : null,
                  }))
                }
                type="checkbox"
              />
              <span className="text-sm text-[var(--color-foreground)]">
                Apply 500-word limit for research idea (default is 100)
              </span>
            </div>
          </div>

          <div className="space-y-2">
            <label
              className="text-sm font-medium text-[var(--color-foreground)]"
              htmlFor="research-idea"
            >
              Research Idea
            </label>
            <textarea
              id="research-idea"
              className="min-h-40 w-full rounded-[var(--radius-md)] border border-[var(--color-border)] bg-white p-3 text-sm leading-6 outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-primary)]"
              onChange={(event) =>
                setDraft((current) => ({ ...current, research_idea: event.target.value }))
              }
              value={draft.research_idea}
            />
            <p
              className={`text-sm ${
                counters.research_idea > researchIdeaLimit
                  ? "text-red-600"
                  : "text-[var(--color-muted-foreground)]"
              }`}
            >
              {counters.research_idea.toLocaleString()} / {researchIdeaLimit.toLocaleString()} words
            </p>
          </div>

          <button
            className="inline-flex h-11 items-center justify-center rounded-[var(--radius-md)] bg-[var(--color-primary)] px-5 text-sm font-medium text-white transition hover:brightness-105 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={Boolean(callError) || isLoadingCalls}
            type="submit"
          >
            Submit
          </button>
        </form>
      </div>
    </main>
  );
}
