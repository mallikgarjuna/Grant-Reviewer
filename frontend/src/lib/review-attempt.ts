export const MAX_SNIPPET_CHARS = 10_000;

type CreateReviewDraft = {
  review_stage: "STEP_1" | "STEP_2";
  call_id: string;
  node_id: string;
  snippet_text: string;
};

export type ReviewAttempt = {
  draft: CreateReviewDraft;
  idempotencyKey: string;
  payloadSha256: string;
  createdAtMs: number;
};

function normalizeSnippetText(value: string): string {
  return value.replace(/\r\n/g, "\n").trim();
}

function normalizeDraft(draft: CreateReviewDraft): CreateReviewDraft {
  return {
    review_stage: draft.review_stage,
    call_id: draft.call_id,
    node_id: draft.node_id,
    snippet_text: normalizeSnippetText(draft.snippet_text),
  };
}

function stableJsonStringify(value: unknown): string {
  if (value === null) {
    return "null";
  }
  if (typeof value === "number" || typeof value === "boolean") {
    return JSON.stringify(value);
  }
  if (typeof value === "string") {
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) {
    return `[${value.map((entry) => stableJsonStringify(entry)).join(",")}]`;
  }
  if (typeof value === "object") {
    const entries = Object.entries(value as Record<string, unknown>)
      .filter(([, nested]) => nested !== undefined)
      .sort(([left], [right]) => left.localeCompare(right));
    const formatted = entries.map(
      ([key, nested]) => `${JSON.stringify(key)}:${stableJsonStringify(nested)}`,
    );
    return `{${formatted.join(",")}}`;
  }
  return "null";
}

function bytesToHex(buffer: ArrayBuffer): string {
  return Array.from(new Uint8Array(buffer))
    .map((byte) => byte.toString(16).padStart(2, "0"))
    .join("");
}

async function sha256Hex(text: string): Promise<string> {
  const bytes = new TextEncoder().encode(text);
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return bytesToHex(digest);
}

function draftsEqual(left: CreateReviewDraft, right: CreateReviewDraft): boolean {
  return (
    left.review_stage === right.review_stage &&
    left.call_id === right.call_id &&
    left.node_id === right.node_id &&
    left.snippet_text === right.snippet_text
  );
}

function parseStoredAttempt(value: string | null): ReviewAttempt | null {
  if (!value) {
    return null;
  }
  try {
    const parsed = JSON.parse(value) as Record<string, unknown>;
    const parsedDraft =
      parsed && typeof parsed === "object" && parsed.draft && typeof parsed.draft === "object"
        ? (parsed.draft as Record<string, unknown>)
        : null;
    const normalizedStage =
      parsedDraft?.review_stage === "STEP_2" ? "STEP_2" : "STEP_1";
    if (
      !parsed ||
      typeof parsed !== "object" ||
      typeof parsed.idempotencyKey !== "string" ||
      typeof parsed.payloadSha256 !== "string" ||
      typeof parsed.createdAtMs !== "number" ||
      !parsedDraft ||
      typeof parsedDraft.call_id !== "string" ||
      typeof parsedDraft.node_id !== "string" ||
      typeof parsedDraft.snippet_text !== "string"
    ) {
      return null;
    }
    return {
      draft: {
        review_stage: normalizedStage,
        call_id: parsedDraft.call_id,
        node_id: parsedDraft.node_id,
        snippet_text: parsedDraft.snippet_text,
      },
      idempotencyKey: parsed.idempotencyKey,
      payloadSha256: parsed.payloadSha256,
      createdAtMs: parsed.createdAtMs,
    };
  } catch {
    return null;
  }
}

const STORAGE_KEY = "gr.review_attempt.v1";

export async function getOrCreateReviewAttempt(
  draft: CreateReviewDraft,
): Promise<ReviewAttempt> {
  const normalizedDraft = normalizeDraft(draft);
  const payloadSha256 = await sha256Hex(stableJsonStringify(normalizedDraft));
  const stored = parseStoredAttempt(sessionStorage.getItem(STORAGE_KEY));

  if (
    stored &&
    stored.payloadSha256 === payloadSha256 &&
    draftsEqual(stored.draft, normalizedDraft)
  ) {
    return stored;
  }

  const nextAttempt: ReviewAttempt = {
    draft: normalizedDraft,
    idempotencyKey: crypto.randomUUID(),
    payloadSha256,
    createdAtMs: Date.now(),
  };
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(nextAttempt));
  return nextAttempt;
}

export function clearReviewAttempt(): void {
  sessionStorage.removeItem(STORAGE_KEY);
}

export function getStoredReviewAttempt(): ReviewAttempt | null {
  return parseStoredAttempt(sessionStorage.getItem(STORAGE_KEY));
}

export async function createNewReviewAttempt(
  draft: CreateReviewDraft,
): Promise<ReviewAttempt> {
  const normalizedDraft = normalizeDraft(draft);
  const payloadSha256 = await sha256Hex(stableJsonStringify(normalizedDraft));
  const nextAttempt: ReviewAttempt = {
    draft: normalizedDraft,
    idempotencyKey: crypto.randomUUID(),
    payloadSha256,
    createdAtMs: Date.now(),
  };
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(nextAttempt));
  return nextAttempt;
}
