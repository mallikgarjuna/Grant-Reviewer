import assert from "node:assert/strict";
import test from "node:test";

import { shouldUseClerkProxy } from "./proxy-routes.ts";

test("protects /app routes", () => {
  assert.equal(shouldUseClerkProxy("/app"), true);
  assert.equal(shouldUseClerkProxy("/app/reviews"), true);
});

test("protects /api/bff routes", () => {
  assert.equal(shouldUseClerkProxy("/api/bff/calls"), true);
  assert.equal(shouldUseClerkProxy("/api/bff/reviews/123"), true);
});

test("bypasses non-protected routes", () => {
  assert.equal(shouldUseClerkProxy("/"), false);
  assert.equal(shouldUseClerkProxy("/blog"), false);
  assert.equal(shouldUseClerkProxy("/privacy"), false);
});
