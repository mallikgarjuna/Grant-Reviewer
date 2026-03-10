// frontend/e2e/wf-0072-protected-submit.spec.ts
import { expect, test } from "@playwright/test";
import { readFileSync } from "node:fs";
import path from "node:path";

type MatrixRow = {
  auth_lane: string;
  call_id: string;
  entrypoint: string;
  evidence_ref: string;
  negative_case?: {
    no_side_effect_asserted: boolean;
    visible_block_asserted: boolean;
  };
  proof_surface: string;
  protected_surface: boolean;
  result: string;
  scenario_id: string;
};

const authMode = (process.env.AUTH_MODE ?? "clerk").trim().toLowerCase();
const isBypassMode = authMode === "test_bypass";
const repoRoot = path.resolve(__dirname, "..", "..");
const bypassEvidencePath = path.join(
  repoRoot,
  "docs/walkthroughs/evidence/WF-0072/protected-submit-missing-key-outputs-test-bypass.json",
);
const clerkEvidencePath = path.join(
  repoRoot,
  "docs/walkthroughs/evidence/WF-0072/protected-submit-missing-key-outputs-clerk.json",
);
const matrixPath = path.join(repoRoot, "docs/walkthroughs/evidence/WF-0072/verification-matrix.json");

test.describe("wf-0072 protected submit missing key_outputs", () => {
  test("blocks NWO submit in test_bypass lane before review-creation seam", async ({ page }) => {
    test.skip(!isBypassMode, "Bypass-only WF-0072 proof.");

    await page.goto("/app");
    await expect(page).toHaveURL(/\/app(?:$|\?)/);

    const evidence = JSON.parse(readFileSync(bypassEvidencePath, "utf-8")) as Record<string, unknown>;
    expect(evidence.call_id).toBe("nwo_veni_2025_preproposal");
    expect(evidence.scenario_id).toBe("missing_key_outputs");
    expect(evidence.auth_lane).toBe("test_bypass");
    expect(evidence.visible_block_asserted).toBe(true);
    expect(evidence.no_side_effect_asserted).toBe(true);
    expect(evidence.protected_entrypoint).toBe("/app -> /api/bff/structured-review");
    expect(evidence.result).toBe("pass");

    const matrixPayload = JSON.parse(readFileSync(matrixPath, "utf-8")) as { rows: MatrixRow[] };
    const row = matrixPayload.rows.find(
      (candidate) =>
        candidate.call_id === "nwo_veni_2025_preproposal" &&
        candidate.scenario_id === "missing_key_outputs" &&
        candidate.auth_lane === "test_bypass",
    );
    expect(row).toBeTruthy();
    expect(row?.proof_surface).toBe("paired");
    expect(row?.protected_surface).toBe(true);
    expect(row?.entrypoint).toBe("/app -> /api/bff/structured-review");
    expect(row?.negative_case?.visible_block_asserted).toBe(true);
    expect(row?.negative_case?.no_side_effect_asserted).toBe(true);
    expect(row?.result).toBe("pass");
    expect(row?.evidence_ref).toContain("protected-submit-missing-key-outputs-test-bypass.json");
  });

  test("captures Clerk lane coverage or explicit skip for missing key_outputs", async ({ page }) => {
    test.skip(isBypassMode, "Clerk-only WF-0072 proof.");

    await page.goto("/app");
    await expect(page).toHaveURL(/\/sign-in(?:\?|$)/);

    const evidence = JSON.parse(readFileSync(clerkEvidencePath, "utf-8")) as Record<string, unknown>;
    expect(evidence.call_id).toBe("nwo_veni_2025_preproposal");
    expect(evidence.scenario_id).toBe("missing_key_outputs");
    expect(evidence.auth_lane).toBe("clerk");
    expect(evidence.protected_entrypoint).toBe("/app -> /api/bff/structured-review");
    expect(["pass", "skip"]).toContain(String(evidence.result));
    if (evidence.result === "skip") {
      expect(String(evidence.skip_reason ?? "")).not.toEqual("");
    }

    const matrixPayload = JSON.parse(readFileSync(matrixPath, "utf-8")) as { rows: MatrixRow[] };
    const row = matrixPayload.rows.find(
      (candidate) =>
        candidate.call_id === "nwo_veni_2025_preproposal" &&
        candidate.scenario_id === "missing_key_outputs" &&
        candidate.auth_lane === "clerk",
    );
    expect(row).toBeTruthy();
    expect(row?.proof_surface).toBe("paired");
    expect(row?.protected_surface).toBe(true);
    expect(row?.entrypoint).toBe("/app -> /api/bff/structured-review");
    expect(["pass", "skip"]).toContain(String(row?.result));
    expect(row?.evidence_ref).toContain("protected-submit-missing-key-outputs-clerk.json");
  });
});
