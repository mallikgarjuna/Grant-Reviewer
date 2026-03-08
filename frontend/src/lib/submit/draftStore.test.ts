// frontend/src/lib/submit/draftStore.test.ts
import { beforeEach, describe, expect, it } from "vitest";

import { loadDraft, saveDraftFiltered } from "@/lib/submit/draftStore";

describe("draftStore", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("saveDraftFiltered_keeps_only_allowed_keys", () => {
    saveDraftFiltered(
      "call-1",
      {
        excellence: "primary",
        abstract: "supporting",
      },
      new Set(["excellence"]),
    );

    expect(loadDraft("call-1")).toEqual({
      excellence: "primary",
    });
  });

  it("saveDraftFiltered_retains_domain_key_only_when_allowed", () => {
    saveDraftFiltered(
      "call-1",
      {
        excellence: "primary",
        __selected_domain: "chemistry",
      },
      new Set(["excellence"]),
    );
    expect(loadDraft("call-1")).toEqual({
      excellence: "primary",
    });

    saveDraftFiltered(
      "call-1",
      {
        excellence: "primary",
        __selected_domain: "chemistry",
      },
      new Set(["excellence", "__selected_domain"]),
    );
    expect(loadDraft("call-1")).toEqual({
      excellence: "primary",
      __selected_domain: "chemistry",
    });
  });

  it("saveDraftFiltered_persists_empty_snapshot_when_allowed_keys_empty", () => {
    saveDraftFiltered(
      "call-1",
      {
        excellence: "primary",
      },
      new Set(),
    );

    expect(loadDraft("call-1")).toEqual({});
  });
});
