type UiMode = "legacy_single_snippet" | "structured_nodes";

export type ReviewFormUiStateInput = {
  isSubmitting: boolean;
  isLoadingCalls: boolean;
  isLoadingConfig: boolean;
  isLoadingNodes: boolean;
  hasSelectedCall: boolean;
  uiMode: UiMode;
  isCallNotFound: boolean;
  configWarning: string | null;
};

export type ReviewFormUiState = {
  showStructuredMessage: boolean;
  showCallNotFoundError: boolean;
  showConfigWarning: boolean;
  disableNodeSelect: boolean;
  disableSnippetInput: boolean;
  disableSubmit: boolean;
};

export function deriveReviewFormUiState(
  input: ReviewFormUiStateInput,
): ReviewFormUiState {
  const isLegacyMode = input.uiMode === "legacy_single_snippet";
  const disableByModeOrCall = !isLegacyMode || input.isCallNotFound;

  return {
    showStructuredMessage: input.uiMode === "structured_nodes",
    showCallNotFoundError: input.isCallNotFound,
    showConfigWarning: Boolean(input.configWarning),
    disableNodeSelect:
      !input.hasSelectedCall ||
      input.isLoadingNodes ||
      input.isSubmitting ||
      input.isLoadingConfig ||
      disableByModeOrCall,
    disableSnippetInput: input.isSubmitting || disableByModeOrCall,
    disableSubmit:
      input.isSubmitting ||
      input.isLoadingCalls ||
      input.isLoadingConfig ||
      disableByModeOrCall,
  };
}
