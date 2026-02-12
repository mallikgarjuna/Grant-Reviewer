# Stage 2: Sample Data & Flow Validation

## Scenario: ERC Starting Grant 2024 — Section B1 Review

This document walks through ONE complete review scenario using minimal sample data.

---

## Sample Data

### 1. FundingAgency
| id | name | short_name |
|----|------|------------|
| `agency-1` | European Research Council | ERC |

### 2. FundingCall
| id | funding_agency_id | name | code | call_year | is_active |
|----|-------------------|------|------|-----------|-----------|
| `call-1` | `agency-1` | ERC Starting Grant 2024 | ERC-2024-STG | 2024 | true |

**aim_objectives**: *"Support excellent PIs at the career stage at which they are starting their own independent research team..."*

### 3. ProposalNode
| id | funding_call_id | parent_node_id | node_type | title | order_index |
|----|-----------------|----------------|-----------|-------|-------------|
| `node-1` | `call-1` | NULL | SECTION | Part B1 | 1 |
| `node-2` | `call-1` | `node-1` | SUBSECTION | Section 1: Extended Synopsis | 1 |
| `node-3` | `call-1` | `node-1` | SUBSECTION | Section 2: Scientific Proposal | 2 |

**ProposalNode `node-2` guidance_text**:
> *"The extended synopsis should give a summary of the proposal, addressing: state-of-the-art and objectives, methodology, and the ground-breaking nature/impact."*

### 4. EvaluationCriterion
| id | funding_call_id | name | order_index |
|----|-----------------|------|-------------|
| `crit-1` | `call-1` | Excellence | 1 |
| `crit-2` | `call-1` | Impact | 2 |

### 5. EvaluationElement
| id | evaluation_criterion_id | name |
|----|-------------------------|------|
| `elem-1` | `crit-1` | Clarity of Objectives |
| `elem-2` | `crit-1` | Soundness of Methodology |
| `elem-3` | `crit-2` | Potential Breakthrough |

### 6. NodeExpectation (Intelligence Layer)
| id | proposal_node_id | evaluation_element_id | expectation_strength | evaluation_intent | guidance_note |
|----|------------------|-----------------------|----------------------|-------------------|---------------|
| `expect-1` | `node-2` | `elem-1` | MANDATORY | COMPLIANCE | "Verify that objectives are explicitly stated and measurable." |
| `expect-2` | `node-2` | `elem-2` | IMPORTANT | QUALITY | "Assess whether the proposed methodology is appropriate for the stated objectives." |
| `expect-3` | `node-2` | `elem-3` | OPTIONAL | STRATEGIC_FIT | "Look for claims of novelty or paradigm shift." |

---

## User Scenario: Reviewing "Extended Synopsis"

### Step 1: User Selects Call & Node
- User selects: `ERC Starting Grant 2024` → `Section 1: Extended Synopsis` (`node-2`)

### Step 2: User Pastes Snippet
User pastes:
> *"This project aims to develop a novel framework for quantum error correction that surpasses current thresholds. We will use a combination of topological codes and machine learning to achieve fault-tolerant computation."*

### Step 3: System Creates Records

**User** (anonymous):
| id | email | is_anonymous |
|----|-------|--------------|
| `user-1` | NULL | true |

**ProposalSnippet**:
| id | user_id | funding_call_id | proposal_node_id | pasted_text | expires_at |
|----|---------|-----------------|------------------|-------------|------------|
| `snippet-1` | `user-1` | `call-1` | `node-2` | *(the pasted text)* | +24h |

### Step 4: System Fetches NodeExpectations
Query: `SELECT * FROM NodeExpectation WHERE proposal_node_id = 'node-2'`
Returns: `expect-1`, `expect-2`, `expect-3`

### Step 5: System Constructs Prompt
Uses:
- `PromptTemplate.template_text` (active version)
- `ProposalNode.guidance_text` → **Proposal Context**
- `NodeExpectation.guidance_note` (for each) → **Evaluation Expectations**
- `ProposalSnippet.pasted_text` → **User Submission**

### Step 6: AI Returns Feedback
AI generates 3 feedback blocks (one per NodeExpectation).

### Step 7: System Saves Review & ReviewCards

**Review**:
| id | proposal_snippet_id | prompt_template_id |
|----|---------------------|--------------------|
| `review-1` | `snippet-1` | `template-1` |

**ReviewCard** (3 cards):
| id | review_id | node_expectation_id | feedback_text |
|----|-----------|---------------------|---------------|
| `card-1` | `review-1` | `expect-1` | "The objectives are stated but lack measurability. Consider quantifying 'surpasses current thresholds.'" |
| `card-2` | `review-1` | `expect-2` | "The methodology mentions 'topological codes and machine learning' but does not explain how they will be combined." |
| `card-3` | `review-1` | `expect-3` | "The claim of 'novel framework' is made but not substantiated with evidence of why existing approaches are insufficient." |

---

## Data Flow Diagram

```
User Action                      System Action
───────────                      ─────────────
Select Call + Node ────────────► Fetch NodeExpectations for node
                                      │
Paste Snippet ─────────────────► Create User (anonymous)
                                 Create ProposalSnippet
                                      │
Click "AI Review" ─────────────► Fetch active PromptTemplate
                                 Assemble prompt (guidance + expectations + snippet)
                                 Call AI API
                                      │
                              ◄────── AI returns structured feedback
                                      │
                                 Create Review
                                 Create ReviewCards (one per NodeExpectation)
                                      │
Display Results ◄──────────────── Return ReviewCards to UI
```

---

## Friction / Ambiguity Identified

### ✅ No Major Issues Found
The schema flows naturally for this scenario.

### ⚠️ Minor Observations

1. **Order of ReviewCards**: The `NodeExpectation.order_index` should determine the display order of `ReviewCard`s in the UI. This requires a JOIN on display.

2. **Empty Expectations**: What if a `ProposalNode` has zero `NodeExpectation` records? Should the system reject the review request, or proceed with a generic prompt?
   - **Suggested Decision**: Reject with error: "No evaluation criteria defined for this section."

3. **AI Output Parsing**: The AI must return feedback structured by `NodeExpectation` ID (or order). This is a prompt engineering concern for Stage 3.

---

## Summary
- **What was built**: Sample data for ERC-2024-STG with 3-level hierarchy.
- **What was validated**: Full data flow from user selection to ReviewCard creation.
- **What remains risky**: AI output parsing and handling nodes with no expectations.
