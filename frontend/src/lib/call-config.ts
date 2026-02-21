type UiMode = "legacy_single_snippet" | "structured_nodes";

export type CallConfigUiState = {
  uiMode: UiMode;
  expectedNodes: string[];
  warningMessage: string | null;
  callNotFound: boolean;
};

type CallConfigPayload = {
  call_logical_id: string;
  config_version: string;
  ui_mode: UiMode;
  expected_nodes?: string[];
};

type ApiResult =
  | { kind: "network_error" }
  | { kind: "http_error"; status: number }
  | { kind: "success"; status: 200; payload: unknown };

const FALLBACK_WARNING =
  "Structured mode could not be loaded. Showing legacy mode instead.";

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function parseCallConfig(payload: unknown): CallConfigPayload | null {
  if (!isRecord(payload)) {
    return null;
  }
  const callLogicalId = payload.call_logical_id;
  const configVersion = payload.config_version;
  const uiMode = payload.ui_mode;
  const expectedNodes = payload.expected_nodes;

  if (
    typeof callLogicalId !== "string" ||
    typeof configVersion !== "string" ||
    (uiMode !== "legacy_single_snippet" && uiMode !== "structured_nodes")
  ) {
    return null;
  }
  if (configVersion !== "1") {
    return null;
  }
  if (uiMode === "structured_nodes") {
    if (!Array.isArray(expectedNodes) || expectedNodes.length === 0) {
      return null;
    }
    if (!expectedNodes.every((item) => typeof item === "string" && item.trim().length > 0)) {
      return null;
    }
    return {
      call_logical_id: callLogicalId,
      config_version: configVersion,
      ui_mode: uiMode,
      expected_nodes: expectedNodes,
    };
  }

  return {
    call_logical_id: callLogicalId,
    config_version: configVersion,
    ui_mode: uiMode,
  };
}

export function resolveCallConfigUiState(result: ApiResult): CallConfigUiState {
  if (result.kind === "network_error") {
    return {
      uiMode: "legacy_single_snippet",
      expectedNodes: [],
      warningMessage: FALLBACK_WARNING,
      callNotFound: false,
    };
  }
  if (result.kind === "http_error") {
    if (result.status === 404) {
      return {
        uiMode: "legacy_single_snippet",
        expectedNodes: [],
        warningMessage: null,
        callNotFound: true,
      };
    }
    return {
      uiMode: "legacy_single_snippet",
      expectedNodes: [],
      warningMessage: FALLBACK_WARNING,
      callNotFound: false,
    };
  }

  const parsed = parseCallConfig(result.payload);
  if (parsed === null) {
    return {
      uiMode: "legacy_single_snippet",
      expectedNodes: [],
      warningMessage: FALLBACK_WARNING,
      callNotFound: false,
    };
  }

  return {
    uiMode: parsed.ui_mode,
    expectedNodes: parsed.expected_nodes ?? [],
    warningMessage: null,
    callNotFound: false,
  };
}
