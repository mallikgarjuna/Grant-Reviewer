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
