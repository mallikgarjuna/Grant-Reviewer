#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Keep core workflow/process docs tool/model agnostic.
mapfile -t WORKFLOW_DOCS < <(
  find "${REPO_ROOT}/docs/workflow" -maxdepth 1 -type f -name "*.md" | sort
)
TARGETS=("${REPO_ROOT}/AGENTS.md" "${WORKFLOW_DOCS[@]}")

# Lowercase patterns; search is case-insensitive.
readonly FORBIDDEN_PATTERN='antigravity|gemini|codex|gpt|claude|cursor|copilot'

violations=0
for path in "${TARGETS[@]}"; do
  if [[ ! -f "$path" ]]; then
    echo "[docs-sanitization] Missing target file: $path"
    violations=1
    continue
  fi

  if rg -n -i -e "$FORBIDDEN_PATTERN" "$path"; then
    echo "[docs-sanitization] Forbidden tool/model reference found in $path"
    violations=1
  fi
done

if [[ "$violations" -ne 0 ]]; then
  echo "[docs-sanitization] FAILED"
  exit 1
fi

echo "[docs-sanitization] PASS"
