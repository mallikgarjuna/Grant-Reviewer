#!/usr/bin/env bash
# scripts/check_docs_sanitization.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Keep core workflow/process docs tool/model agnostic.
if [[ -n "${DOCS_SANITIZATION_TARGETS:-}" ]]; then
  IFS=':' read -r -a TARGETS <<<"${DOCS_SANITIZATION_TARGETS}"
else
  mapfile -t WORKFLOW_DOCS < <(
    find "${REPO_ROOT}/docs/workflow" -maxdepth 1 -type f -name "*.md" | sort
  )
  TARGETS=("${REPO_ROOT}/AGENTS.md" "${WORKFLOW_DOCS[@]}")
fi

# Lowercase patterns; search is case-insensitive.
readonly FORBIDDEN_PATTERN='antigravity|gemini|codex|gpt|claude|cursor|copilot'

violations=0
if command -v rg >/dev/null 2>&1; then
  SEARCH_CMD=("rg" "-n" "-i" "-e" "$FORBIDDEN_PATTERN")
else
  SEARCH_CMD=("grep" "-n" "-E" "-i" "$FORBIDDEN_PATTERN")
fi

for path in "${TARGETS[@]}"; do
  if [[ ! -f "$path" ]]; then
    echo "[docs-sanitization] Missing target file: $path"
    violations=1
    continue
  fi

  if "${SEARCH_CMD[@]}" "$path"; then
    echo "[docs-sanitization] Forbidden tool/model reference found in $path"
    violations=1
  fi
done

if [[ "$violations" -ne 0 ]]; then
  echo "[docs-sanitization] FAILED"
  exit 1
fi

echo "[docs-sanitization] PASS"
