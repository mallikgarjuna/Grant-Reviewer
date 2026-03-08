<!-- docs/brainstorms/qna/brainstorm-QnA-WF-0067-review-trust-surface-closure.md -->
# WF-0067 — Review Trust Surface Closure

Artifact: brainstorm-qna
Version: v0.2
Status: Draft Complete
Last Updated: 2026-03-08

## Kickoff + Direct-Start Narrowing

This Phase 0 run used direct-start synthesis from the user's explicit brief plus live repo artifacts, rather than a multi-turn interview. The selections below record the narrowing logic that became contract in the main brainstorm.

### Q1: What is the primary remaining launch blocker after WF-0065 and WF-0066?

- A) More backend contract hardening across the wedge.
- B) Researcher trust in the review experience itself.
  Improve the user-visible review surfaces so a researcher can tell what was evaluated, what it maps to, what it is based on, and what was not evaluated.
- C) Broader call/funder expansion.

> Recommendation: B. WF-0065 and WF-0066 already close the strongest contract-correctness and scope-truth gaps. A is dismissed because it repeats recently closed work unless a user-visible trust surface requires a small contract addition. C is dismissed because it violates the permanent NWO/ERC/MSCA wedge.
> Selected: B (derived from user brief + repo reality check)

### Q2: Which trust gaps are actually launch-blocking?

- A) Weak official source-basis visibility, weak reviewed-vs-supporting-vs-not-reviewed labeling, and weak limitation copy.
- B) Lack of richer scoring/explanation polish.
- C) Missing extraction and onboarding guidance.

> Recommendation: A. These are the gaps most likely to make a researcher distrust or over-trust the output. B is useful but can wait because it improves polish more than truthfulness. C is explicitly out of scope for this workflow and not required to make the current review output honest.
> Selected: A (derived from user brief + repo reality check)

### Q3: What is the smallest workflow that materially improves trust?

- A) Review only the review detail page and the minimum BFF/API fields needed to render it honestly.
- B) Redesign the whole app trust model across submit, history, landing, and review flows.
- C) Build a generic provenance/explainability system first.

> Recommendation: A. It directly targets the decisive researcher moment with the smallest blast radius. B is dismissed as feature creep. C is dismissed as architecture-first overreach that delays user-visible improvement.
> Selected: A (derived from user brief + repo reality check)

### Q4: Which user-facing surfaces should this WF target?

- A) Review cards, section/group labels, coverage summary, official source-basis visibility, and limitation/boundary copy.
- B) Only a top-of-page warning banner.
- C) Mostly backend correctness work with little UI change.

> Recommendation: A. Trust must be legible where the researcher actually reads the feedback. B is too weak because the cards would still feel opaque. C is dismissed because this workflow is explicitly about user-visible trust and truthful usefulness.
> Selected: A (derived from user brief + repo reality check)

### Q5: What must stay explicitly out of scope?

- A) New calls, assisted extraction, generic platform hardening, broad explainability architecture, and supporting-context expansion beyond honest labeling.
- B) Nothing; keep it flexible and discover scope during implementation.
- C) All backend changes, even if a small contract addition is needed to render trust surfaces truthfully.

> Recommendation: A. The workflow needs hard edges to stay credible and reviewable. B is dismissed because it invites feature creep. C is too rigid because a small review-detail contract addition may be the minimum honest path to surface source basis or boundary states.
> Selected: A (derived from user brief + repo reality check)

### Part B audit tightening applied

- Locked representative proof set explicitly to `nwo_veni_2025_preproposal`, `erc_stg_2026_full`, and `MSCA-PF-2025`.
- Narrowed `source basis` to authoritative official-call metadata only, with explicit fail-closed behavior when unavailable.
