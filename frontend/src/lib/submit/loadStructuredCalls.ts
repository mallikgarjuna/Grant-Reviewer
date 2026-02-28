import type { CallSummary, CallConfigResponse } from "@/lib/bff/types";

export type StructuredCallsWarningReason =
  | "timeout"
  | "http_error"
  | "network_error"
  | "invalid_response";

export type StructuredCallsWarning = {
  callCode: string;
  reason: StructuredCallsWarningReason;
};

type LoadStructuredCallsInput = {
  calls: CallSummary[];
  fetchImpl?: typeof fetch;
  timeoutMs?: number;
  concurrency?: number;
};

type LoadStructuredCallsResult = {
  calls: CallSummary[];
  warnings: StructuredCallsWarning[];
};

function withTimeout<T>(promise: Promise<T>, timeoutMs: number): Promise<T> {
  return new Promise<T>((resolve, reject) => {
    const timeoutHandle = globalThis.setTimeout(() => {
      reject(new Error("timeout"));
    }, timeoutMs);
    promise.then(
      (value) => {
        globalThis.clearTimeout(timeoutHandle);
        resolve(value);
      },
      (error: unknown) => {
        globalThis.clearTimeout(timeoutHandle);
        reject(error);
      },
    );
  });
}

function isStructuredConfig(payload: unknown): payload is CallConfigResponse {
  if (!payload || typeof payload !== "object") {
    return false;
  }
  const candidate = payload as Partial<CallConfigResponse>;
  return candidate.ui_mode === "structured_nodes";
}

async function loadOneCall(
  call: CallSummary,
  fetchImpl: typeof fetch,
  timeoutMs: number,
): Promise<{ call: CallSummary | null; warning: StructuredCallsWarning | null }> {
  try {
    const response = await withTimeout(
      fetchImpl(`/api/bff/calls/${encodeURIComponent(call.code)}/config`, {
        method: "GET",
        cache: "no-store",
      }),
      timeoutMs,
    );
    if (!response.ok) {
      return {
        call: null,
        warning: {
          callCode: call.code,
          reason: "http_error",
        },
      };
    }
    const parsed = (await response.json()) as unknown;
    if (!isStructuredConfig(parsed)) {
      return {
        call: null,
        warning: null,
      };
    }
    return { call, warning: null };
  } catch (error) {
    const reason =
      error instanceof Error && error.message === "timeout"
        ? "timeout"
        : "network_error";
    return {
      call: null,
      warning: {
        callCode: call.code,
        reason,
      },
    };
  }
}

export async function loadStructuredCalls(
  input: LoadStructuredCallsInput,
): Promise<LoadStructuredCallsResult> {
  const fetchImpl = input.fetchImpl ?? fetch;
  const timeoutMs = input.timeoutMs ?? 4_000;
  const concurrency = input.concurrency ?? 4;
  const calls = input.calls;

  const eligible: CallSummary[] = [];
  const warnings: StructuredCallsWarning[] = [];
  let cursor = 0;

  async function worker(): Promise<void> {
    while (cursor < calls.length) {
      const currentIndex = cursor;
      cursor += 1;
      const result = await loadOneCall(calls[currentIndex], fetchImpl, timeoutMs);
      if (result.call) {
        eligible.push(result.call);
      }
      if (result.warning) {
        warnings.push(result.warning);
      }
    }
  }

  const workers = Array.from({ length: Math.min(concurrency, calls.length) }).map(() =>
    worker(),
  );
  await Promise.all(workers);
  const orderById = new Map(calls.map((call, index) => [call.id, index]));
  eligible.sort((left, right) => (orderById.get(left.id) ?? 0) - (orderById.get(right.id) ?? 0));
  return { calls: eligible, warnings };
}
