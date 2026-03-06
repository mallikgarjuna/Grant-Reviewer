#!/usr/bin/env bash
set -euo pipefail

# Keep core workflow/process docs tool/model agnostic.
readonly TARGETS=(
  "AGENTS.md"
  "docs/workflow/README.md"
  "docs/workflow/phase-0-0-start-workflow.md"
  "docs/workflow/phase-1-1-prd-generate.md"
  "docs/workflow/phase-2-1-task-generate.md"
)

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
