// frontend/src/lib/submit/draftStore.ts
const DRAFT_KEY_PREFIX = "draft_universal_submit";

function buildDraftKey(callId: string): string {
  return `${DRAFT_KEY_PREFIX}_${callId}_v1`;
}

export function loadDraft(callId: string): Record<string, string> {
  if (!callId) {
    return {};
  }
  const raw = window.localStorage.getItem(buildDraftKey(callId));
  if (!raw) {
    return {};
  }
  try {
    const parsed = JSON.parse(raw) as unknown;
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
      return {};
    }
    return Object.entries(parsed).reduce<Record<string, string>>((acc, [key, value]) => {
      if (typeof value === "string") {
        acc[key] = value;
      }
      return acc;
    }, {});
  } catch {
    return {};
  }
}

export function saveDraft(callId: string, draft: Record<string, string>): void {
  if (!callId) {
    return;
  }
  window.localStorage.setItem(buildDraftKey(callId), JSON.stringify(draft));
}

export function saveDraftFiltered(
  callId: string,
  draft: Record<string, string>,
  allowedKeys: ReadonlySet<string>,
): void {
  if (!callId) {
    return;
  }
  const filteredDraft = Object.entries(draft).reduce<Record<string, string>>(
    (acc, [key, value]) => {
      if (allowedKeys.has(key)) {
        acc[key] = value;
      }
      return acc;
    },
    {},
  );
  window.localStorage.setItem(buildDraftKey(callId), JSON.stringify(filteredDraft));
}

export function clearDraft(callId: string): void {
  if (!callId) {
    return;
  }
  window.localStorage.removeItem(buildDraftKey(callId));
}
