// frontend/e2e/wf-0072-nwo-happy-path.spec.ts
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
};

const authMode = (process.env.AUTH_MODE ?? "clerk").trim().toLowerCase();
const isBypassMode = authMode === "test_bypass";
const repoRoot = path.resolve(__dirname, "..", "..");
const evidencePath = path.join(
  repoRoot,
  "docs/walkthroughs/evidence/WF-0072/nwo_veni_2025_preproposal_happy_path_test_bypass.json",
);
const matrixPath = path.join(repoRoot, "docs/walkthroughs/evidence/WF-0072/verification-matrix.json");

test.describe("wf-0072 nwo protected happy path", () => {
  test("records deterministic test_bypass proof on protected path", async ({ page }) => {
    test.skip(!isBypassMode, "Bypass-only WF-0072 proof.");

    await page.goto("/app");
    await expect(page).toHaveURL(/\/app(?:$|\?)/);

    const evidence = JSON.parse(readFileSync(evidencePath, "utf-8")) as Record<string, unknown>;
    expect(evidence.call_id).toBe("nwo_veni_2025_preproposal");
    expect(evidence.auth_lane).toBe("test_bypass");
    expect(evidence.protected_entrypoint).toBe("/app -> /api/bff/structured-review");
    expect(evidence.result).toBe("pass");

    const matrixPayload = JSON.parse(readFileSync(matrixPath, "utf-8")) as { rows: MatrixRow[] };
    const row = matrixPayload.rows.find(
      (candidate) =>
        candidate.call_id === "nwo_veni_2025_preproposal" &&
        candidate.scenario_id === "happy_path" &&
        candidate.auth_lane === "test_bypass",
    );
    expect(row).toBeTruthy();
    expect(row?.proof_surface).toBe("paired");
    expect(row?.protected_surface).toBe(true);
    expect(row?.entrypoint).toBe("/app -> /api/bff/structured-review");
    expect(row?.result).toBe("pass");
    expect(row?.evidence_ref).toContain("nwo_veni_2025_preproposal_happy_path_test_bypass.json");
  });
});
