# Launch Checklist (Neon + Render + Vercel + Clerk)

**Status**: Draft (v0.1)
**Last updated**: 2026-02-12

This checklist is intentionally MVP-focused and biased toward “ship safely with minimal moving parts”.

## 0) One-time decisions (confirm before launch)

- **LLM mode**: keep `LLM_MODE=stub` until launch day, then flip to `openai` when ready to incur cost.
- **DB connection**: use Neon **direct** connection string for Render (pooler + extra SSL options caused intermittent failures).
- **Bootstrap path**: Render free tier has **no shell** → run bootstrap scripts from a developer machine against Neon.

## 1) Secrets & env vars

### Backend (Render)

- `DATABASE_URL` (Neon **direct** URL; `sslmode=require`; avoid `channel_binding=require`)
- `BFF_SHARED_SECRET` (must match Vercel)
- `CLERK_SECRET_KEY` (server-side Clerk key)
- `CLERK_PUBLISHABLE_KEY` (if backend needs it; otherwise omit)
- `CLERK_JWKS_URL` or `CLERK_ISSUER` (only if required by current backend auth setup)
- `LLM_MODE` (`stub` pre-launch; `openai` on launch day)
- `OPENAI_API_KEY` (only if `LLM_MODE=openai`)
- Any quota/kill-switch envs used by the API (if present in code)

### Frontend (Vercel)

- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
- `CLERK_SECRET_KEY` (only if your Next.js server routes need it)
- `FASTAPI_BASE_URL` (Render URL, e.g. `https://grant-reviewer.onrender.com`)
- `BFF_SHARED_SECRET` (must match Render)

## 2) Neon setup

- Use a **direct** connection string for the deployed backend.
- Ensure the Neon compute is not suspended when testing (wakes on demand; first query can be slow).

### Local note: don’t `source .env` if values include `&`

If your `DATABASE_URL` contains query params (e.g. `...&sslmode=require...`), `source backend/.env` may fail.
Prefer either:
- setting env vars via `export DATABASE_URL='...'`, or
- relying on `python-dotenv` (backend entrypoint loads `.env`).

## 3) Production bootstrap (run from developer machine)

Run these from repo root with the Neon **direct** `DATABASE_URL` used by Render:

```bash
cd backend
export DATABASE_URL='postgresql://...'

uv run python scripts/ensure_prompt_template.py
uv run python scripts/ingest_call.py data/calls/legacy/erc/erc_cog_2026_full_official.yaml
```

Verify bootstrap via deployed API:

```bash
curl -i https://grant-reviewer.onrender.com/health
curl -i https://grant-reviewer.onrender.com/health/db
curl -i https://grant-reviewer.onrender.com/calls
```

## 4) Smoke tests (deployed)

### Backend (Render)

- `GET /health` returns `200 {"ok":true}`
- `GET /health/db` returns `200 {"ok":true}` (or `503` if DB down; that’s expected readiness semantics)
- `GET /calls` returns `200` with at least one call after bootstrap

### Frontend (Vercel + Clerk)

- Logged-out `GET /app` redirects to sign-in (Clerk)
- Logged-in flow:
  - `/app` loads
  - create review succeeds (stub mode)
  - results page renders and is refresh-safe

### BFF boundary safety

- Direct unsigned access to protected backend endpoints should fail (e.g. `GET /reviews/{id}` → `401`).

## 5) Launch-day flip (when ready for real LLM)

Backend (Render):

- Set `LLM_MODE=openai`
- Ensure `OPENAI_API_KEY` is present
- Deploy

Then do a one-shot end-to-end test from the frontend UI and capture:
- request time (browser Network tab)
- review status `COMPLETED`

## 6) Rollback plan (fast)

- If OpenAI is unstable or too slow: set `LLM_MODE=stub` and redeploy backend.
- If DB connectivity issues recur: re-check Neon URL is **direct** and does not include `channel_binding=require`.

## 7) References

- Walkthrough: `docs/walkthroughs/walkthrough_task_8.0C_deployment_wiring.md`
- Lessons: `docs/lessons.md` (Neon/Render + dotenv gotchas)
