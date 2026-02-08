# Q&A History

## 2026-02-06

### Q: Hierarchy structure for proposal nodes?
**A**: Use a generic `ProposalNode` table with `parent_id` recursive relationship for arbitrary depth.

### Q: MVP persistence model?
**A**: Anonymous sessions. User record created per session with `is_anonymous=true`, cascade-deleted after TTL (24h).

### Q: Are evaluation criteria shared across calls?
**A**: No. Strictly per-call in MVP. Each `EvaluationElement` belongs to one `FundingCall`.

### Q: Should we store full prompt/model state?
**A**: Not for MVP. Focus on linking ReviewCards to NodeExpectation IDs for traceability.

### Q: ReviewCard links to EvaluationElement or NodeExpectation?
**A**: NodeExpectation. Provides full context (strength, intent, guidance_note).

### Q: Two guidance fields - what's the difference?
**A**: 
- `ProposalNode.guidance_text`: What the applicant should write
- `NodeExpectation.guidance_note`: What the reviewer should look for

### Q: What if a node has zero NodeExpectations?
**A**: Reject with error: "No evaluation criteria defined for this section." (AD 2.1)

### Q: Tech stack for backend?
**A**: SQLModel (ORM), UV (package manager), FastAPI (API framework for Stage 4+).

## 2026-02-07

### Q: How to support UI "traffic light" indicators?
**A**: Added a typed `rating` field (`ReviewRating` Enum) to `ReviewCard`. This allows the UI to render findings based on severity (Critical, Warning, etc.) without string parsing. (AD 4.1)

### Q: How to handle async AI latency in the UI?
**A**: Added `Review.status` (Pending/Completed/Failed). The UI can poll this status before fetching results. (AD 4.2)

### Q: Does the system provide an overall verdict?
**A**: Yes. Added `Review.overall_summary` and `Review.overall_rating` (calculated as the highest severity among individual findings). (AD 4.2 & 4.3)

### Q: "In SQLModel, the table name is plural while the class name is singular. Is this correct?"
**A:** Yes, this is the industry standard convention for ORMs.
- **Class (`FundingAgency`)**: Represents a *single object* (row) in memory.
- **Table (`funding_agencies`)**: Represents a *collection* (set) of records in the database.
Using plural for classes (`FundingAgencies`) would be confusing as the object instance is singular.

## 2026-02-08

### Q: What does it mean by adding `!` prefix in `.gitignore` files?
**A:** `!` negates a previous ignore rule (“un-ignores” a path). Git evaluates rules top-to-bottom; a later `!pattern` can re-include files/dirs ignored earlier. If a parent dir is ignored, you must also unignore the parent (and sometimes `/**`) so Git will descend into it.

### Q: Clarify phase terminology used in artifacts and commits.
**A:** Standardized pipeline naming:
- **Phase 0** = Brainstorming
- **Phase 1** = PRD creation
- **Phase 2** = Task breakdown creation
- **Phase 3** = Task implementation and verification

### Q: Where should process rules be stored for Codex work in this repo?
**A:** Use `AGENTS.md` as the primary source for Codex workflow instructions in this project.

### Q: Should Phase 3 commits happen after each subtask (e.g., 7.1, 7.2)?
**A:** Yes. During Phase 3, commit after each completed subtask with a short message that includes the subtask ID.

### Q: How are we going to approach building the rest of the app?
**A:** API-first with a minimal FastAPI surface first, then UI. Next major slice is **Task 7.0 (FastAPI MVP)**: add discovery endpoints (calls + nodes) and a `POST /reviews` endpoint that wraps the existing `ReviewerService`, followed by tests and then a thin frontend.
