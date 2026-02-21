import assert from "node:assert/strict";
import test from "node:test";

import { deriveReviewFormUiState } from "./review-form-ui-state.ts";

test("legacy state enables normal submission path", () => {
  const state = deriveReviewFormUiState({
    isSubmitting: false,
    isLoadingCalls: false,
    isLoadingConfig: false,
    isLoadingNodes: false,
    hasSelectedCall: true,
    uiMode: "legacy_single_snippet",
    isCallNotFound: false,
    configWarning: null,
  });

  assert.equal(state.showStructuredMessage, false);
  assert.equal(state.showCallNotFoundError, false);
  assert.equal(state.showConfigWarning, false);
  assert.equal(state.disableNodeSelect, false);
  assert.equal(state.disableSnippetInput, false);
  assert.equal(state.disableSubmit, false);
});

test("structured mode shows blocked message and disables submit controls", () => {
  const state = deriveReviewFormUiState({
    isSubmitting: false,
    isLoadingCalls: false,
    isLoadingConfig: false,
    isLoadingNodes: false,
    hasSelectedCall: true,
    uiMode: "structured_nodes",
    isCallNotFound: false,
    configWarning: null,
  });

  assert.equal(state.showStructuredMessage, true);
  assert.equal(state.disableNodeSelect, true);
  assert.equal(state.disableSnippetInput, true);
  assert.equal(state.disableSubmit, true);
});

test("fallback warning keeps legacy flow while surfacing warning", () => {
  const state = deriveReviewFormUiState({
    isSubmitting: false,
    isLoadingCalls: false,
    isLoadingConfig: false,
    isLoadingNodes: false,
    hasSelectedCall: true,
    uiMode: "legacy_single_snippet",
    isCallNotFound: false,
    configWarning: "Structured mode could not be loaded.",
  });

  assert.equal(state.showConfigWarning, true);
  assert.equal(state.disableSnippetInput, false);
  assert.equal(state.disableSubmit, false);
});

test("404 call-not-found disables all submission controls", () => {
  const state = deriveReviewFormUiState({
    isSubmitting: false,
    isLoadingCalls: false,
    isLoadingConfig: false,
    isLoadingNodes: false,
    hasSelectedCall: true,
    uiMode: "legacy_single_snippet",
    isCallNotFound: true,
    configWarning: null,
  });

  assert.equal(state.showCallNotFoundError, true);
  assert.equal(state.disableNodeSelect, true);
  assert.equal(state.disableSnippetInput, true);
  assert.equal(state.disableSubmit, true);
});
