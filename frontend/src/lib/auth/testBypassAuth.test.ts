// frontend/src/lib/auth/testBypassAuth.test.ts
import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  buildTestBypassToken,
  getAuthMode,
  getTestBypassConfigError,
  resolveBypassUserId,
} from "@/lib/auth/testBypassAuth";

describe("testBypassAuth", () => {
  beforeEach(() => {
    vi.unstubAllEnvs();
    vi.useRealTimers();
  });

  it("defaults auth mode to clerk", () => {
    expect(getAuthMode()).toBe("clerk");
  });

  it("rejects bypass mode in production", () => {
    vi.stubEnv("AUTH_MODE", "test_bypass");
    vi.stubEnv("NODE_ENV", "production");
    vi.stubEnv("TEST_AUTH_SECRET", "dev-secret");
    expect(getTestBypassConfigError()).toBe("TEST_BYPASS_FORBIDDEN_IN_PRODUCTION");
  });

  it("accepts signed bypass token from cookie", async () => {
    vi.stubEnv("AUTH_MODE", "test_bypass");
    vi.stubEnv("NODE_ENV", "test");
    vi.stubEnv("TEST_AUTH_SECRET", "dev-secret");
    vi.setSystemTime(new Date("2026-03-08T12:00:00Z"));
    const token = await buildTestBypassToken("test_user_1", 1_772_971_200);
    const request = new Request("http://localhost/api/bff/calls", {
      headers: {
        cookie: `gr_test_auth=${encodeURIComponent(token)}`,
      },
    });

    await expect(resolveBypassUserId(request)).resolves.toBe("test_user_1");
  });

  it("rejects expired bypass token", async () => {
    vi.stubEnv("AUTH_MODE", "test_bypass");
    vi.stubEnv("NODE_ENV", "test");
    vi.stubEnv("TEST_AUTH_SECRET", "dev-secret");
    vi.stubEnv("TEST_AUTH_MAX_AGE_SECONDS", "60");
    vi.setSystemTime(new Date("2026-03-08T12:00:00Z"));
    const token = await buildTestBypassToken("test_user_1", 1_772_971_000);
    const request = new Request("http://localhost/api/bff/calls", {
      headers: {
        cookie: `gr_test_auth=${encodeURIComponent(token)}`,
      },
    });

    await expect(resolveBypassUserId(request)).resolves.toBeNull();
  });
});
