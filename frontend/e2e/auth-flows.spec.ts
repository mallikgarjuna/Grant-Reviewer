// frontend/e2e/auth-flows.spec.ts
import { expect, test } from "@playwright/test";

const authMode = (process.env.AUTH_MODE ?? "clerk").trim().toLowerCase();
const isBypassMode = authMode === "test_bypass";

test.describe("auth flow smoke", () => {
  test("homepage CTA reaches app in test_bypass mode", async ({ page }) => {
    test.skip(!isBypassMode, "Bypass-only smoke.");

    await page.goto("/");
    await page.getByRole("link", { name: "Check My Draft Now" }).first().click();
    await expect(page).toHaveURL(/\/app(?:$|\?)/);
    await expect(page.getByRole("heading", { name: "Run a Grant Review" })).toBeVisible();
  });

  test("protected app redirects unauthenticated users in clerk mode", async ({ page }) => {
    test.skip(isBypassMode, "Clerk-only auth gate check.");

    await page.goto("/app");
    await expect(page).toHaveURL(/\/sign-in(?:\?|$)/);
    await expect(
      page.getByRole("heading", { name: /Authentication config is missing|Sign in/i }),
    ).toBeVisible();
  });

  test("credentialed login redirects to app in clerk mode", async ({ page }) => {
    test.skip(isBypassMode, "Clerk-only login flow.");

    const email = process.env.E2E_CLERK_TEST_EMAIL?.trim() ?? "";
    const password = process.env.E2E_CLERK_TEST_PASSWORD?.trim() ?? "";
    test.skip(!email || !password, "Set E2E_CLERK_TEST_EMAIL and E2E_CLERK_TEST_PASSWORD.");

    await page.goto("/sign-in?redirect_url=%2Fapp");
    await page.locator('input[name="identifier"]').fill(email);
    await page.getByRole("button", { name: /continue/i }).click();
    await page.locator('input[name="password"]').fill(password);
    await page.getByRole("button", { name: /continue/i }).click();
    await expect(page).toHaveURL(/\/app(?:$|\?)/);
    await expect(page.getByRole("heading", { name: "Run a Grant Review" })).toBeVisible();
  });
});
