<!-- docs/brainstorms/brainstorm-WF-0067-review-trust-surface-closure.md -->
# WF-0067 — Review Trust Surface Closure

Artifact: brainstorm
Version: v0.3
Status: Draft Complete
Last Updated: 2026-03-08

Q&A transcript (archived): `docs/brainstorms/qna/brainstorm-QnA-WF-0067-review-trust-surface-closure.md`

---

## Contract Safety (SSOT)

- This brainstorm is the SSOT for WF-0067 scope and contract decisions.
- The Q&A transcript is rationale only; it must not introduce new contracts.
- If later planning adds or changes a trust-surface contract, promote it here and log it in `docs/logs/decisions.md`.

---

## 1. Problem Statement

Full Q&A transcript: `docs/brainstorms/qna/brainstorm-QnA-WF-0067-review-trust-surface-closure.md` (Kickoff + Direct-Start Narrowing)

- PeerLens now has stronger call-contract correctness across the locked NWO/ERC/MSCA wedge, but a real researcher can still see a trust gap in the review experience itself.
- The current review page shows review cards, criterion names, and a coverage summary, but it still leaves too much of the trust story implicit:
  - a card does not clearly show its official source basis,
  - reviewed-vs-supporting-vs-not-reviewed boundaries are page-level and easy to miss,
  - limitation messaging is too weak about what the system did not evaluate,
  - user-visible traceability is not yet strong enough to make revision decisions feel defensible.
- The critical product risk is no longer "is the base contract wired correctly?" The critical risk is "will a researcher believe this output is honest, bounded, and worth acting on?"

Contract Notes / Non-obvious constraints:

- This WF starts after WF-0063, WF-0064, WF-0065, and WF-0066. It must not reopen their solved contract-correctness scope.
- The target problem is researcher-facing trust in review outputs, not internal platform confidence or broad launch checklist cleanup.

## 2. Desired Outcome

- A researcher should be able to inspect a review result and answer four questions quickly:
  - which evaluation criterion/element this feedback maps to,
  - which proposal section was actually reviewed,
  - what official call basis the system is relying on,
  - what was explicitly not evaluated in this review.
- After this WF, the review experience should feel narrow but truthful rather than broad but ambiguous.
- The result should materially improve launch readiness inside the locked wedge without widening scope into new calls, extraction, or generic platform work.

Section 2 decisions:

- Success is improved researcher trust in the existing review output, not higher model sophistication.
- The preferred outcome is explicit trust messaging on review results rather than more hidden backend hardening.
- Launch-readiness value comes from making the current product legible and honest, not from claiming broader coverage.

## 3. Target User / Actor

- Primary actor: a researcher reviewing PeerLens feedback for an NWO, ERC, or MSCA submission slice and deciding whether to revise based on it.
- Secondary actor: a maintainer validating whether the product is truthfully launch-ready within the locked wedge.
- This WF is not primarily for admins, onboarding, or marketing surfaces.

Section 3 decisions:

- Optimize first for the moment after a review completes.
- Use one trust standard across the locked NWO/ERC/MSCA wedge, even if copy details stay call-aware.
- Treat review detail as the decisive launch surface because that is where a researcher judges usefulness.

## 4. Rough Idea (Unstructured Thinking)

## Repo Reality Snapshot (Read-Only) (2026-03-08)

- `frontend/src/app/app/reviews/[reviewId]/page.tsx` already exposes a coverage summary and some honest boundary text such as `Visible but not part of this review`, but that honesty is concentrated in one summary block rather than carried through the card-level reading flow.
- `frontend/src/components/review/ReviewCard.tsx` shows criterion, evaluation element, reviewer focus, and rating, but does not show a clear official source basis, does not foreground the reviewed proposal section, and does not explain what kind of claim the card is making.
- `backend/app/schemas/api.py` already returns useful trust-adjacent fields such as `node_title`, `criterion`, `criterion_description`, `evaluation_element_name`, `expectation_guidance_note`, `assessment_status`, and `not_assessable_reason`, but the frontend does not use all of them to make trust legible.
- `frontend/src/app/api/bff/reviews/[reviewId]/route.ts` already normalizes `detail_state` plus review-detail array fields for the page, so any trust-surface contract change must cross the backend response seam and this BFF normalization seam rather than stopping at schema-only edits.
- `backend/app/repositories/review_repository.py` currently resolves `supporting_context_node_logical_ids` to an empty list even when supporting nodes exist, which means truthful supporting-context labeling is not yet a proven wedge-wide backend contract.
- Canonical call definitions already carry `source_hint` for evaluation criteria/elements across NWO/ERC/MSCA, which suggests a viable user-facing source-basis surface exists without broadening into reviewer-policy/rule provenance or new call authoring.
- Existing completed workflows prove contract correctness and fail-closed boundaries, but they do not yet prove that a researcher can understand what a review card is grounded in and what is outside the review.

Open questions suggested by repo snapshot:

- Is page-level coverage summary enough, or must trust context appear directly on each review card?
- What is the minimum source-basis disclosure that improves trust without overwhelming the page?
- Which limitations are launch-blocking to explain, and which can stay deferred?
- Can this WF stay centered on review detail plus its backing BFF/API contract, or does it need submit-flow copy too?

Section 4 decisions:

- Narrow the WF to `review detail + review card trust surfaces` only.
- Prefer surfacing already-available or call-derived basis metadata over inventing a new explanation system.
- Keep the main change set user-visible and localized to the post-review experience.

Contract Notes / Non-obvious constraints:

- Representative proof scope is locked to the same one-call-per-family baseline already used for wedge proof: `nwo_veni_2025_preproposal`, `erc_stg_2026_full`, and `MSCA-PF-2025`.
- This WF must not imply that one polished single-call experience is enough to claim wedge-wide trust closure.

## 5. Constraints

- Scope lock is permanent: active planning stays inside NWO/ERC/MSCA only.
- Do not widen into assisted extraction, new funding-program coverage, generic telemetry/platform hardening, or prompt-quality tuning.
- Do not change core review semantics unless a trust surface cannot be made honest without a small contract addition on the review-detail path.
- Source-basis visibility must fail closed:
  - show authoritative official-call metadata when available,
  - never invent or infer basis text from model output,
  - show an explicit unavailable/legacy limitation when authoritative basis is missing.
- Preserve the distinction between:
  - reviewed sections,
  - supporting/visible but not reviewed sections,
  - sections with no generated cards,
  - findings that are `NOT_ASSESSABLE`.
- Only label a surface as `supporting context` when authoritative review-detail metadata supplies that role; otherwise fail closed to `reviewed` vs `not reviewed` without inferring supporting semantics from page-local heuristics.
- Researcher-facing wording must use `evaluation criteria/elements`, not `rubric`.

Section 5 decisions:

- The narrow target surface is the review detail page and the BFF/API fields required to render it honestly.
- Any backend work in this WF must serve user-visible trust directly.
- The workflow should remain implementable without reopening engine architecture or call-definition onboarding.
- Legacy or mixed-version review records must remain honest: if authoritative call linkage or source-basis metadata is unavailable, the UI must say so rather than simulate full trust coverage.

## 6. Risks / Unknowns

- The WF could sprawl into a generic explainability or provenance system if "source basis" is not tightly defined.
- Overloading each card with too much metadata could hurt readability and reduce usefulness.
- If the page-level limitations panel is vague, the WF may still look polished while leaving the core trust gap unresolved.
- If the trust contract is defined only in copy, without tests proving correct reviewed/not-reviewed labeling across the wedge, launch claims will still be weak.
- If Phase 1 ignores the backend response-assembly seam or the BFF normalization seam, schema-only changes can look complete on paper while never reaching the live review page.

Section 6 decisions:

- Define source basis narrowly: official call basis for the evaluation criterion/element, not full model-chain provenance.
- Treat reviewed/not-reviewed boundary honesty as launch-blocking.
- Treat richer explanatory prose, better scores, and broader history/export improvements as non-blocking.

## Open Questions / Deferred

- Exact visual treatment of trust metadata on each card. Deferred to Phase 1.
- Whether the page needs a compact "How to read this review" explainer versus only inline labels. Deferred to Phase 1.
- Whether ERC stage-specific limitation copy needs a dedicated variant beyond a shared trust pattern. Deferred to Phase 1.

## 7. MVP Definition

- Smallest WF that materially improves trust:
  - target only the review detail experience,
  - make every review card clearly identify the reviewed section and mapped evaluation criterion/element,
  - expose a concise official source-basis line where available,
  - make page-level boundary/limitation messaging explicit about what was reviewed and what was not,
  - label reviewed vs supporting vs not reviewed surfaces truthfully, but only claim `supporting context` when the review-detail contract explicitly provides that role,
  - avoid changing engine behavior unless required to expose this trust contract on the review-detail path.
- Launch-blocking trust gaps for this WF:
  - weak or missing official source-basis visibility,
  - weak or fragmented reviewed-vs-supporting-vs-not-reviewed labeling,
  - weak limitation copy about what the review did not evaluate.
- Nice-to-have but non-blocking gaps:
  - more polished scoring language,
  - richer card explanations beyond the minimum trust basis,
  - broader export/history improvements,
  - submit-flow educational copy not required for post-review truthfulness.

Section 7 decisions:

- WF-0067 should target these user-facing surfaces:
  - review cards,
  - section/group headers,
  - coverage summary,
  - source-basis visibility,
  - limitation/boundary copy about what was and was not evaluated.
- The WF should not attempt assisted extraction, supporting-context semantics expansion, or new call coverage.
- The minimum acceptable proof of improvement is cross-representative honesty on the locked wedge, not one polished single-call demo.
- Source-basis visibility in this WF means official call-basis disclosure tied to the mapped evaluation criterion/element or equivalent authoritative review-detail metadata, not full LLM-chain provenance.
- When both criterion-level and evaluation-element-level `source_hint` values exist, Phase 1 resolves the card-level source-basis precedence to `evaluation element source_hint` first, then `criterion source_hint`, and otherwise an explicit unavailable or legacy limitation state.
- Boundary honesty must keep `visible but not reviewed` distinct from `no generated cards`, because both are non-reviewed surfaces but they communicate different trust limitations to the researcher.

Required evidence before claiming WF-0067 is done:

- Automated contract tests proving the backend review-detail response assembly and the BFF review-detail payload expose the trust fields the UI depends on for exactly `nwo_veni_2025_preproposal`, `erc_stg_2026_full`, and `MSCA-PF-2025`.
- Frontend tests proving:
  - review cards show mapped evaluation criterion/element plus reviewed section context,
  - source-basis visibility renders correctly when available,
  - source-basis visibility fails closed when unavailable or when the review detail is legacy/fallback-linked,
  - reviewed/supporting/not-reviewed labeling is truthful and does not infer supporting-context labels when the contract does not provide them,
  - limitation copy appears for the required states,
  - `NOT_ASSESSABLE` cards remain explicitly labeled.
- Tests or fixture-backed evidence covering fail-closed limitation states at the actual response seams, including `legacy_fallback`, unavailable source basis, and any representative mixed-version/compatibility case used to justify trust copy.
- Manual review evidence or fixture-backed screenshots for those exact representative calls showing the trust pattern is understandable and not misleading.
- Explicit proof that no out-of-scope expansion occurred into new calls, extraction, or generic platform work.

## 8. Explicit Non-Goals

- New funding-program expansion outside NWO/ERC/MSCA.
- Assisted extraction, `.docx`/`.pdf` ingestion, or confidence-preview flows.
- Generic explainability architecture, model-chain provenance, or platform observability work.
- Reopening WF-0063/WF-0064 supporting-context semantics beyond truthful labeling of current review boundaries.
- Broader prompt retuning, score redesign, or history/export redesign unless directly required by the trust surfaces above.
