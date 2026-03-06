<!-- docs/memory/tools/frontend.md -->
# Frontend Tooling

- **NVM requirements:** Use `nvm use` (which uses `.nvmrc`) before running `npm` or `npx`. If there is no `nvm`, scaffold/build locally and commit the generated `frontend/` directory.
- **2026-03-06:** Hierarchical-call support is still client-blocked in `frontend/src/lib/submit/renderModel.ts` via `nested_nodes`, while review detail already has partial call-aware ordering/label support via `call_id` + fetched call nodes. Why: future sessions should treat nested submit as the main frontend bottleneck, not restart review detail from zero.
