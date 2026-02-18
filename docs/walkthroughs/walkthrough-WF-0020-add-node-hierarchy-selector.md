# WF-0020 — Add node hierarchy selector

Artifact: walkthrough
Version: v0.1
Status: Completed
Last Updated: 2026-02-18

## Summary

Implemented a parent-first node hierarchy selector in the `/app` submit flow. The previous flat `Proposal Section` dropdown is now split into:
- `Parent Section` selector
- `Proposal Section` selector filtered by selected parent

The implementation preserves existing submit payload behavior (`node_id` remains the selected child node ID) and adds deterministic fallback handling for nodes with missing/unresolvable parent metadata under `Other Sections`.

## Files Changed

- `frontend/src/app/app/page.tsx`
- `frontend/src/lib/node-hierarchy.ts`
- `docs/tasks/task-WF-0020-add-node-hierarchy-selector.md`

## How To Run

1. Start backend:
```bash
cd backend
LLM_MODE=stub uv run uvicorn main:app --reload
```
2. Start frontend:
```bash
cd frontend
npm run dev
```
3. Open:
- `http://localhost:3000/app`

## Verification

Executed in this environment:
- `cd frontend && npm run lint`
- `pre-commit run --all-files`

Manual verification checklist (to run locally):
1. Choose a funding call with many nodes and confirm `Parent Section` must be selected before child node selection.
2. Confirm child options update when changing parent and stale child selection clears.
3. Confirm ambiguous child names include parent-context suffixes where needed.
4. Confirm nodes with missing/unresolvable parent map under `Other Sections`.
5. Submit a review and confirm request still sends valid selected child `node_id`.

## Known Limitations

- Local browser-based manual checks were not executed inside this environment.
- Fallback grouping for incomplete hierarchy metadata is deterministic but may be less semantically precise than fully modeled hierarchy data.
