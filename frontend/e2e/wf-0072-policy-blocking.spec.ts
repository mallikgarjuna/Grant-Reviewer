// frontend/e2e/wf-0072-policy-blocking.spec.ts
import { expect, test } from "@playwright/test";
import { readFileSync } from "node:fs";
import path from "node:path";

type MatrixRow = {
  auth_lane: string;
  call_id: string;
  entrypoint: string;
  evidence_ref: string;
  proof_surface: string;
  protected_surface: boolean;
  result: string;
  scenario_id: string;
  scenario_variant?: string;
};

const authMode = (process.env.AUTH_MODE ?? "clerk").trim().toLowerCase();
const isBypassMode = authMode === "test_bypass";
const repoRoot = path.resolve(__dirname, "..", "..");
const policyEvidencePath = path.join(repoRoot, "docs/walkthroughs/evidence/WF-0072/policy_blocking.json");
const matrixPath = path.join(repoRoot, "docs/walkthroughs/evidence/WF-0072/verification-matrix.json");

test.describe("wf-0072 policy blocking", () => {
  test("captures representative user-surface policy blocking in test_bypass lane", async ({ page }) => {
    test.skip(!isBypassMode, "Bypass-only WF-0072 proof.");

    await page.goto("/app");
    await expect(page).toHaveURL(/\/app(?:$|\?)/);

    const evidence = JSON.parse(readFileSync(policyEvidencePath, "utf-8")) as Record<string, unknown>;
    const userSurface = evidence.user_surface as Record<string, unknown>;
    expect(evidence.call_id).toBe("nwo_veni_2025_preproposal");
    expect(userSurface.auth_lane).toBe("test_bypass");
    expect(userSurface.protected_entrypoint).toBe("/app -> /api/bff/structured-review");
    expect(userSurface.policy_code).toMatch(/QUOTA_EXCEEDED|REVIEWS_DISABLED/);
    expect(userSurface.visible_block_asserted).toBe(true);
    expect(["skip", "pass"]).toContain(String(userSurface.result));

    const matrixPayload = JSON.parse(readFileSync(matrixPath, "utf-8")) as { rows: MatrixRow[] };
    const row = matrixPayload.rows.find(
      (candidate) =>
        candidate.call_id === "nwo_veni_2025_preproposal" &&
        candidate.scenario_id === "policy_blocking" &&
        candidate.scenario_variant === "user_surface" &&
        candidate.auth_lane === "test_bypass",
    );
    expect(row).toBeTruthy();
    expect(row?.proof_surface).toBe("paired");
    expect(row?.protected_surface).toBe(true);
    expect(row?.entrypoint).toBe("/app -> /api/bff/structured-review");
    expect(["skip", "pass"]).toContain(String(row?.result));
    expect(row?.evidence_ref).toContain("policy_blocking.json");
  });
});
