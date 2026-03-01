# WF-0043 — NWO Veni 2025 Preproposal: Single-Call MVP Hardening

Artifact: brainstorm
Version: v0.3
Status: Draft Complete
Last Updated: 2026-03-01

Q&A transcript (archived): `docs/brainstorms/qna/brainstorm-QnA-WF-0043-nwo-veni-2025-preproposal-single-call-mvp-harden.md`

---

## Contract Safety (SSOT)

- This brainstorm is the **SSOT for contracts/decisions** (what we will implement).
- The Q&A transcript is **rationale only**; it must not introduce new contracts.
- Any contract changes must preserve:
  - API error semantics/idempotency (notably `IDEMPOTENCY_PAYLOAD_MISMATCH` and existing 4xx/5xx mappings)
  - `/app/reviews` persistence behavior (review record creation + status transitions)

---

## Repo Reality Snapshot (Read-Only) (2026-03-01)

- Backend create endpoints: `POST /api/structured-review` (structured multi-node) and `POST /reviews` (single-snippet).
- Both endpoints enforce `Idempotency-Key` + payload hash (`request_payload_sha256`); mismatch returns `IDEMPOTENCY_PAYLOAD_MISMATCH`.
- Reviews are persisted early (review row created before engine work); execution failures appear as `review.status=FAILED` with an `overall_summary` message rather than an API error for many runtime/LLM/policy failure modes.
- Reviewer-policy enforcement is in `backend/app/services/review_execution_core.py`:
  - `POST_CHECK` + `BLOCKING` run deterministic forbidden-term scans on LLM feedback text
  - `BLOCKING` triggers up to 2 attempts, then fails with `POLICY_BLOCKING`
- Existing tests already cover many related seams (`backend/tests/test_api.py`, `backend/tests/test_review_execution_core.py`, `backend/tests/test_structured_reviewer_service.py`), but the “hardening target” (trust + regression bundle) is not yet captured as a single explicit contract suite.

## Open Questions / Deferred (Phase 0.1)

Resolved in Sections 1–2:
- Primary hardening target: `POST /api/structured-review` for `nwo_veni_2025_preproposal` only.
- Verification bundle = docs appendix + explicit pytest subset + small fixture matrix.
- Primary “trust” risk = contract drift (error semantics + idempotency + persistence).

Still deferred (explicitly):
- TTL-expiry reuse test strategy (document semantics; assert replay+mismatch within TTL).
- A scenario table enumerating, per case: expected HTTP status + error code (or 200), whether a Review row must exist, and expected ReviewStatus/`overall_summary` convention if persisted.

---

## 1. Problem Statement

Hardening needed for the single-call MVP for `nwo_veni_2025_preproposal`:
- Preserve API error semantics + idempotency invariants.
- Preserve review persistence + failure-state semantics used by `/app/reviews`.
- Add confidence that reviewer-policy enforcement (blocking/post-check/prompt-only) cannot silently regress.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0043-nwo-veni-2025-preproposal-single-call-mvp-harden.md` (Section 1)

### Decisions (Section 1)

- Hardening target flow: `POST /api/structured-review` for `nwo_veni_2025_preproposal` only. (Q1)
- Primary “trust” risk: **contract drift** (error semantics + idempotency + persistence). (Q2)
- Execution-time failure contract (after Review row exists): persist Review + return `200` `{review_id, status}` on service/engine execution failures (timeout/engine-contract/engine-exec failures), with stable failure summary conventions in `overall_summary`. Endpoint-level request/validation errors return API errors and must not create a Review. (Q3)
- Regression hardening mechanism: deterministic `pytest` contract suite (API + service seams) using a stubbed LLM client. (Q4)
- Deterministic verification bundle = docs checklist + explicit pytest subset + a versioned fixture matrix. (Q5)

### Contract Notes / Non-obvious constraints (Section 1)

- “Preserve API error semantics” explicitly includes:
  - `Idempotency-Key` required behavior
  - `IDEMPOTENCY_PAYLOAD_MISMATCH` semantics and status mapping
  - existing validation ordering (avoid changing which error code wins for multi-error payloads)
- “Preserve `/app/reviews` persistence” explicitly includes:
  - review row creation and status transitions remain compatible with the UI’s “review exists even if execution fails” expectations
  - avoid changing side effects (e.g., creating duplicate reviews) while tightening tests
- Persistence-on-failure applies only **after** a Review row is created inside the service layer; request/validation errors that return API errors must **not** create a Review.

---

## 2. Desired Outcome

After WF-0043, we can say “this call won’t silently regress” because:

- `POST /api/structured-review` contract is locked by deterministic API contract tests (success + representative failures + idempotency replay/mismatch).
- The user-visible persistence semantics for `/app/reviews` are locked:
  - review exists even when execution fails
  - failures are represented via `ReviewStatus=FAILED` + stable `overall_summary` conventions
- Idempotency semantics are locked:
  - same key + same payload → same persisted review returned
  - same key + different payload → `IDEMPOTENCY_PAYLOAD_MISMATCH`
  - TTL reuse behavior is documented and tested (where feasible under current test harness)
- Reviewer-policy enforcement semantics for this call are regression-locked via deterministic tests around the single-snippet execution seam (blocking vs post-check vs prompt-only), without changing runtime behavior.
- A “deterministic verification bundle” exists (docs appendix + explicit pytest subset + small fixture matrix) so a maintainer can re-verify quickly before/after changes.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0043-nwo-veni-2025-preproposal-single-call-mvp-harden.md` (Section 2)

---

## 3. Target User / Actor

Primary actor: maintainers/engineers.

User-facing surface we protect (by preserving contracts): applicants using `/app/reviews` and the universal submit/review flow for this call.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0043-nwo-veni-2025-preproposal-single-call-mvp-harden.md` (Section 3)

Contract Notes / Non-obvious constraints:
- The “trust” deliverable is not a new feature; it is a repeatable, deterministic *verification bundle* that blocks regressions pre-merge.
- Tests must be safe-by-default: isolated test DB only; no real LLM network calls.

---

## 4. Rough Idea (Unstructured Thinking)

Deliver a single-call hardening package with three parts:

1) A focused API contract test suite for `POST /api/structured-review` for `nwo_veni_2025_preproposal`.
2) A small adjacent set of deterministic tests for reviewer-policy enforcement semantics (blocking/post-check/prompt-only) in the single-snippet execution seam (call-specific, no behavior change).
3) A deterministic verification bundle appendix (docs + commands + fixture matrix) that a maintainer can run quickly.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0043-nwo-veni-2025-preproposal-single-call-mvp-harden.md` (Section 4)

Contract Notes / Non-obvious constraints:
- Avoid brittle “content quality” assertions; assert contracts (error codes, idempotency replay, persistence invariants, stable failure summaries).
- Fixture matrix must be grounded in `nwo_veni_2025_preproposal` nodes/constraints/policy rules only.

---

## 5. Constraints

- Scope atomic: single-call MVP hardening for `nwo_veni_2025_preproposal` only.
- Preserve:
  - API error semantics (code + status mapping + validation ordering)
  - idempotency semantics (replay/mismatch/TTL)
  - `/app/reviews` persistence behavior (review exists even if execution fails; status and summary semantics stable)
- No new tooling (no Playwright/Cypress) unless separately approved.
- Prefer “tests first”; refactor only when required to make tests deterministic and fast.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0043-nwo-veni-2025-preproposal-single-call-mvp-harden.md` (Section 5)

---

## 6. Risks / Unknowns

- Risk: accidental dependence on dev DB or real LLM calls → flaky/unsafe tests.
- Risk: changing persistence timing/shape breaks `/app/reviews` behavior even if API responses look “fine”.
- Risk: idempotency regressions under conflict/race paths create duplicate persisted reviews.
- Risk: reviewer-policy enforcement can silently drift if not explicitly asserted.
- Unknown/possible deferral: TTL expiry reuse semantics may be hard to test without time control; must still be documented.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0043-nwo-veni-2025-preproposal-single-call-mvp-harden.md` (Section 6)

---

## Open Questions / Deferred

- TTL expiry reuse: document semantics; assert replay+mismatch within TTL; skip expiry-time travel without adding time-control tooling.
- Keep the fixture matrix small (8–12 cases); do not expand into a full endpoint decision-table project in this WF.

---

## 7. MVP Definition

If shipping in 2–3 days, WF-0043 ships:

- Deterministic API contract tests for `POST /api/structured-review` (single call) covering:
  - success
  - representative validation failures (unknown node IDs, stage mismatch, missing idempotency key, etc.)
  - idempotency replay + payload mismatch
  - persistence invariants:
    - API error paths do **not** persist Review rows
    - execution-layer failures after review creation persist `FAILED` reviews with stable `overall_summary` conventions
- Deterministic policy-enforcement regression tests for this call (single-snippet seam), covering:
  - blocking vs post-check vs prompt-only semantics
  - stable failure summary conventions when blocking persists as `FAILED`
- Deterministic verification bundle (docs appendix + pytest subset + fixture matrix)

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0043-nwo-veni-2025-preproposal-single-call-mvp-harden.md` (Section 7)

---

## 8. Explicit Non-Goals

- No new UI/UX work and no browser/E2E automation tooling.
- No multi-call expansion.
- No prompt/model tuning “quality improvements” that can’t be asserted deterministically.
- No behavior changes to existing API error semantics/idempotency/persistence unless a real regression bug is identified and fixed under test.

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0043-nwo-veni-2025-preproposal-single-call-mvp-harden.md` (Section 8)

---

## Appendix — Deterministic Verification Bundle (v0.1)

### What this WF locks

- `POST /api/structured-review` contract (single call: `nwo_veni_2025_preproposal`):
  - error codes/status mapping and validation ordering
  - idempotency replay + payload mismatch semantics
  - review persistence invariants used by `/app/reviews`
- Reviewer-policy enforcement semantics for this call in the single-snippet seam:
  - `BLOCKING` vs `POST_CHECK` vs `PROMPT_ONLY` behavior remains stable

### How to run (local)

DB isolation rule: never run tests against the dev DB. Use the test docker compose file and set `DATABASE_URL` accordingly.

Suggested flow:

```sh
cd backend
docker compose -f docker-compose.test.yml up -d
export DATABASE_URL=...  # must match backend/docker-compose.test.yml; never use dev DB
uv run pytest -q
```

WF-0043 contract subset (to be implemented in Phase 3):

```sh
cd backend
uv run pytest -q -k wf_0043  # target: a small, focused contract suite added in this WF
```

### Fixture matrix (target)

Target fixture location (to be created in Phase 3): `backend/tests/fixtures/wf_0043_contract_matrix.yaml`

- 8–12 parametrized cases:
  - success
  - missing `Idempotency-Key`
  - idempotency replay (same payload)
  - idempotency payload mismatch
  - unknown node ID
  - review stage mismatch
  - representative quota/disabled cases (as applicable)
  - policy blocking + post-check warning cases (single-snippet seam)

### Scenario table (to fill as cases are implemented)

For each case in the fixture matrix, record:
- HTTP: status + (error.code | `200`)
- Persistence: Review row created? (yes/no)
- If persisted: expected `ReviewStatus` + `overall_summary` convention (prefix/category; not exact string)
