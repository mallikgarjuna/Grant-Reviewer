import assert from "node:assert/strict";
import test from "node:test";

import { resolveCallConfigUiState } from "./call-config.ts";

test("returns structured mode for valid structured payload", () => {
  const state = resolveCallConfigUiState({
    kind: "success",
    status: 200,
    payload: {
      call_logical_id: "nwo_veni_2025_preproposal",
      config_version: "1",
      ui_mode: "structured_nodes",
      expected_nodes: ["academic_profile"],
    },
  });

  assert.deepEqual(state, {
    uiMode: "structured_nodes",
    expectedNodes: ["academic_profile"],
    warningMessage: null,
    callNotFound: false,
  });
});

test("falls back with warning for malformed success payload", () => {
  const state = resolveCallConfigUiState({
    kind: "success",
    status: 200,
    payload: {
      call_logical_id: "nwo_veni_2025_preproposal",
      config_version: "1",
      ui_mode: "structured_nodes",
    },
  });

  assert.equal(state.uiMode, "legacy_single_snippet");
  assert.equal(state.callNotFound, false);
  assert.ok(state.warningMessage);
});

test("returns call-not-found state for 404", () => {
  const state = resolveCallConfigUiState({
    kind: "http_error",
    status: 404,
  });

  assert.deepEqual(state, {
    uiMode: "legacy_single_snippet",
    expectedNodes: [],
    warningMessage: null,
    callNotFound: true,
  });
});

test("falls back with warning for unsupported config version", () => {
  const state = resolveCallConfigUiState({
    kind: "success",
    status: 200,
    payload: {
      call_logical_id: "nwo_veni_2025_preproposal",
      config_version: "2",
      ui_mode: "legacy_single_snippet",
    },
  });

  assert.equal(state.uiMode, "legacy_single_snippet");
  assert.ok(state.warningMessage);
  assert.equal(state.callNotFound, false);
});

test("falls back with warning for unknown ui_mode", () => {
  const state = resolveCallConfigUiState({
    kind: "success",
    status: 200,
    payload: {
      call_logical_id: "nwo_veni_2025_preproposal",
      config_version: "1",
      ui_mode: "future_mode",
    },
  });

  assert.equal(state.uiMode, "legacy_single_snippet");
  assert.ok(state.warningMessage);
  assert.equal(state.callNotFound, false);
});

test("falls back with warning when structured payload has invalid expected_nodes", () => {
  const state = resolveCallConfigUiState({
    kind: "success",
    status: 200,
    payload: {
      call_logical_id: "nwo_veni_2025_preproposal",
      config_version: "1",
      ui_mode: "structured_nodes",
      expected_nodes: ["academic_profile", ""],
    },
  });

  assert.equal(state.uiMode, "legacy_single_snippet");
  assert.ok(state.warningMessage);
  assert.equal(state.callNotFound, false);
});
