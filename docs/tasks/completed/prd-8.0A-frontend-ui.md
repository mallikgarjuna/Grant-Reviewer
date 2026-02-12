# PRD 8.0A: Frontend UI Slice (Next.js App + MDX + BFF Adapter)

**Date**: 2026-02-09
**Task ID**: 8.0A
**Pipeline Phase**: Phase 1 (PRD)
**Status**: Draft (v0.6 - Revised)
**Last Updated**: 2026-02-09

## Summary

Build the first end-to-end web UI for Grant Reviewer using Next.js (App Router) with a strict BFF boundary to the existing FastAPI backend. The MVP delivers:
- Public marketing + MDX blog for SEO discovery.
- Authenticated app flow to run snippet reviews.
- A BFF adapter layer that signs requests to FastAPI, enforces idempotency requirements, and maps canonical backend errors into UI-safe results.

This PRD is intentionally scoped to the minimum that enables Task 8.0A Phase 3 implementation and a usable MVP slice.

## Background / Context

- Backend contracts are already implemented (Task 8.0B): signed request headers, ownership checks, required `Idempotency-Key`, quota enforcement, kill switch, canonical errors.
- This task focuses on building the UI and the minimal Next-side plumbing required to consume those contracts safely.

Related artifacts:
- Phase 0 notes: `docs/brainstorms/brainstorming-8.0A-frontend-ui.md`
- Contract PRD: `docs/tasks/completed/prd-8.0B-bff-contracts.md`

## Decisions Locked (MVP, to unblock Phase 2)

### Identity mapping (Clerk -> FastAPI)

- Canonical `external_user_id` sent to FastAPI is the Clerk user id: `clerk_user_id = auth().userId` (or equivalent Clerk server API).
- FastAPI receives this value as `X-GR-User-Id` and uses it for:
  - review ownership enforcement
  - idempotency uniqueness
  - quota accounting

### Where signing happens (and why)

- All FastAPI calls are made from Next.js server-side code only (route handlers / server actions).
- The BFF adapter is the single owner of:
  - constructing request bytes
  - signing those exact bytes
  - making the fetch call
  - parsing canonical errors

Rationale: minimizes “same JSON, different bytes” failures and keeps request construction consistent across endpoints.

### Idempotency persistence scope

- Persist the “current attempt” in `sessionStorage` (tab-scoped by browser design).
- This means:
  - refresh safety within the same tab is supported
  - new tab is a new, independent attempt (acceptable for MVP; no cross-tab coordination)

### Deliverable separation (to protect critical path)

- `8.0A.0` scaffolding (must land before UI pages): Next scaffold + Clerk + adapter + noindex guardrail.
- `8.0A.1` app vertical slice pages (`/app`, `/app/reviews/[id]`).
- `8.0A.2` marketing/MDX polish (non-blocking for app slice).

### Optional skills (guardrails, not requirements)

If you want extra best-practice guardrails during Phase 3 implementation, install these skills locally (requires Node/npm):
- `npx skills add vercel-labs/agent-skills@vercel-react-best-practices -g -y`
- `npx skills add https://github.com/addyosmani/web-quality-skills --skill accessibility -g -y`

Notes:
- These are guidance-only and must not expand MVP scope.
- If installed, we’ll consult them before/while implementing `8.0A.0a2` and `8.0A.1`.

### MVP visual style (locked)

Use this style baseline for Phase 3 implementation:
- Primary color: `#2563EB`
- Neutral palette: slate / blue-gray
- Font: Inter (headings + body)
- Border radius: medium-rounded (`12px` to `16px`)
- Spacing density: comfortable -> slightly airy
- Theme mode: light-only (MVP)

Interaction principles:
- Clarity over cleverness: each screen should answer “what do I do next?”
- Trust and calm: neutral surfaces, minimal shadows, restrained color usage.
- Speed feel: snappy hover/press states, short micro-animations, avoid heavy visual effects.
- One primary action per screen; secondary/tertiary actions visually de-emphasized.

## Goals (MVP)

- Ship an authenticated app that can create and view reviews:
  - calls -> nodes -> snippet -> submit -> results
- Ensure browser never calls FastAPI directly; Next server routes act as BFF.
- Ensure resubmits and refreshes are safe (idempotency key persistence) and do not accidentally multiply cost.
- Keep `/app/*` private and not indexed, while marketing/blog are indexable.

## Non-Goals (Explicitly Deferred)

- Payments, subscriptions, paid tiers, org accounts, sharing links.
- Background jobs, polling, streaming responses.
- Repo-wide lint debt cleanup (tracked as Task 8.1+).
- Full analytics integration (vendor wiring); keep placeholder only.
- E2E suite (Playwright) beyond minimal guardrails.

## Users / Primary Use Cases

- Public visitor reads a marketing page or blog post and clicks “Try it”.
- Authenticated user runs a snippet review and sees results.
- Authenticated user opens a deep link to an existing review and sees results (or “not found” if not owned).

## UX Scope

### Public (SEO)
- `/` marketing landing page
- `/blog/*` MDX articles

### App (auth required)
- `/app` submission flow (call picker, node picker, snippet input, submit)
- `/app/reviews/[review_id]` results page

Auth behavior:
- Unauthenticated user hitting `/app/*` is redirected to Clerk sign-in and returned to the intended destination after login.

## Technical Scope

### BFF boundary (hard requirement)

- Browser talks only to Next.js routes/actions.
- Next.js server code calls FastAPI server-to-server.
- FastAPI base URL is server-only; no `NEXT_PUBLIC_*` exposure.

### Adapter layer (first-class deliverable)

Implement a single adapter module that is the only place that knows:
- `FASTAPI_BASE_URL`
- how to sign requests (HMAC with `BFF_SHARED_SECRET`)
- how to parse canonical errors (`{error:{code,message,details}}`)

The adapter returns UI-safe types:
- `Ok<T>` for success
- `Err<ApiError>` for canonical errors

#### Adapter API surface (locked for MVP)

The adapter must expose exactly these MVP functions (typed):
- `listCalls() -> Result<CallsResponse>`
- `listNodes(callId: string) -> Result<NodesResponse>`
- `createReview(payload: {call_id: string; node_id: string; snippet_text: string}, attempt: Attempt) -> Result<CreateReviewResponse>`
- `getReview(reviewId: string) -> Result<ReviewDetailResponse>`

Where:
- `Attempt` contains:
  - `idempotencyKey` (string)
  - `payloadSha256` (string)
  - `createdAtMs` (number)

Notes:
- `createReview` must set `Idempotency-Key` header and use the attempt persistence rules below.
- Return type `Result<T>` is a discriminated union so UI never branches on HTTP status.

### Signing (locked decision)

The adapter signs the exact request bytes it sends to FastAPI:
- Build body bytes once.
- Compute signature over `sha256(body_bytes)`.
- Send those same `body_bytes` in the request.

Timestamp skew policy (MVP):
- Use current server time in seconds for `X-GR-Timestamp`.
- On `UNAUTHORIZED` due to expiry, show a generic “session expired” message and prompt re-login; do not retry automatically.

### Idempotency (locked decision)

FastAPI requires `Idempotency-Key` for `POST /reviews`. Next must implement:
- Attempt persistence in `sessionStorage`:
  - draft: `{call_id,node_id,snippet_text}`
  - `idempotency_key`, `payload_sha256`, `created_at_ms`
- Payload hashing normalization:
  - normalize newlines (`\r\n` -> `\n`)
  - trim leading/trailing whitespace
- Reuse rule:
  - unchanged payload -> reuse stored key (safe retry/refresh)
  - changed payload -> generate new key (new attempt)
- FAILED retry rule:
  - always generate a new key
  - prefill inputs for convenience

### Synchronous submission UX (MVP)

- `POST /reviews` is synchronous.
- UI shows an in-flight state and disables submit while in-flight.
- After ~40s show a “still working, refresh safely” message.
- No automatic retries.

Timeout alignment (MVP):
- Backend targets ~30s for LLM execution; UI message at 40s is informational, not a hard cancel.
- MVP behavior does not cancel in-flight requests; user may refresh and safely resubmit using the same attempt key (if inputs unchanged).

### SEO privacy guardrails (MVP)

- `/app/*` should not be indexed:
  - `robots.txt` disallows `/app/`
  - `X-Robots-Tag: noindex` for `/app/*`

Verification guardrail (MVP, concrete):
- Add a small script (shell or node) that:
  - fetches `/robots.txt` and asserts it contains `Disallow: /app/`
  - fetches a representative app route (e.g., `/app`) and asserts `X-Robots-Tag: noindex`
- For MVP, run it as part of the Phase 3 “Verify” checklist (CI integration can come later).

## Error Handling Requirements (UI)

UI should branch on canonical `error.code`, not HTTP status.

Required UX handling:
- `UNAUTHORIZED`: redirect to sign-in (or show sign-in CTA).
- `QUOTA_EXCEEDED`: show limit reached and reset time if present in `details.reset_at`.
- `REVIEWS_DISABLED`: show maintenance state.
- `VALIDATION_ERROR`, `SNIPPET_TOO_LONG`, `NO_EXPECTATIONS`, etc.: show inline form errors.
- `REVIEW_NOT_FOUND`: show “Not found”.

Review states:
- `FAILED` is rendered as a state (with retry CTA), not as an exception screen.

## Acceptance Criteria

### A. App flow
- User can load `/app`, select call and node, paste snippet, submit, and navigate to results.
- User can open `/app/reviews/[review_id]` directly and see the same result.
- Cross-user review access results in “Not found” (backend returns masked 404).

### B. Cost/abuse safety
- UI never calls FastAPI directly from the browser.
- All FastAPI calls are signed through the adapter.
- `POST /reviews` always includes `Idempotency-Key`.
- Refresh + resubmit with unchanged draft reuses the same key (no duplicate spend).
- FAILED retry uses a new key.

### C. SEO/privacy
- Marketing/blog routes are indexable.
- `/app/*` is not indexable via both `robots.txt` and `X-Robots-Tag: noindex`.
- A lightweight verification step exists for the above and is executed during Phase 3 verification.

### D. UX resilience (sync)
- Submit is disabled during in-flight.
- After ~40s, user sees a clear “still working / refresh safely” message.
- No automatic retry behavior exists.

### E. Accessibility (MVP baseline)
- Form inputs have labels (or accessible names).
- Buttons/inputs are keyboard reachable with visible focus.
- Error messages are readable and associated to the relevant input.
- Color contrast follows WCAG AA targets for text and controls.

## Dependencies

- Clerk configuration for Next.js (sign-in, callbacks, and redirect preservation).
- Backend env shared secret alignment:
  - `BFF_SHARED_SECRET` in FastAPI
  - same secret available to Next server-side code
- Frontend tooling:
  - Node.js `22.17.0` and npm available for scaffolding/building `frontend/`
  - When `nvm` exists in the environment, run `nvm use v22.17.0` before any `npm`/`npx` commands
  - If the execution environment cannot run Node tooling, scaffold locally and commit the generated `frontend/` files, then continue implementation changes normally.

## Out of Scope Ideas (Backlog)

- Public share links, org/team accounts, paid tiers.
- Background job processing with polling/streaming.
- Proactive quota introspection endpoint and UI.
- Strict ESLint rules that hard-block non-adapter FastAPI calls (after first slice is stable).
- Cross-tab idempotency coordination (keep MVP tab-scoped; revisit if needed).
- CI-enforced SEO privacy checks (run manually first, automate later).

## Verification Plan (Phase 3)

- Manual smoke:
  - submit review once -> results
  - refresh `/app` with same draft -> resubmit uses same idempotency key
  - FAILED retry -> new key (verify new review id)
  - deep link `/app/reviews/[id]` without prior submit
- Adapter invariants:
  - run the adapter invariant self-check (payload normalization stability + signature changes when bytes change)
- Lightweight SEO check:
  - confirm `/robots.txt` and `/app/*` `X-Robots-Tag` behavior

## Revision History

- **v0.1** (2026-02-09): Initial PRD for the 8.0A UI slice; incorporates locked Phase 0 decisions on idempotency persistence, signing exact bytes, sync UX, and SEO noindex guardrails.
- **v0.2** (2026-02-09): Locked Clerk identity mapping, centralized signing/request-bytes ownership in the adapter, clarified tab-scoped idempotency persistence, specified adapter API surface, aligned timeout expectations, and made the SEO verification guardrail concrete.
- **v0.3** (2026-02-09): Added optional skill-based guardrails (Next/React best practices, accessibility) and locked a minimal accessibility acceptance baseline for MVP.
- **v0.4** (2026-02-09): Updated accessibility skill reference to match installed `web-quality-skills` accessibility skill.
- **v0.5** (2026-02-09): Added explicit Node tooling dependency/fallback and required adapter invariant verification as part of Phase 3 verify.
- **v0.6** (2026-02-09): Added explicit `nvm use v22.17.0` step for environments that use `nvm` to expose `npm/npx`.
- **v0.7** (2026-02-09): Locked concrete MVP visual style choices (color, typography, spacing, radius, light-only theme) and interaction principles.
