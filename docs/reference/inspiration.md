# PeerLens — Competitor & Inspiration Research

Reference this file during brainstorming with:
`@docs/reference/inspiration.md`

This research analyzes direct competitors in the AI grant space and analog competitors in the broader academic writing ecosystem. Use these patterns to inform UI/UX and messaging.

---

## 🎯 Direct Competitors

| Competitor | URL | Hook / Value Prop | Trust Strategy | Key Takeaway (Steal) |
|---|---|---|---|---|
| **Grantease** | [grantease.io](https://www.grantease.io/) | "Writing a proposal shouldn't take hours" | NIH/Scientific specialized AI models | **15-Min Review Phase**: Explicitly frames "Review Your First Draft" as a distinct 15-min task. |
| **Grantable** | [grantable.co](https://www.grantable.co/) | "AI-Powered Grant Success" | Clean, modern UI with trusted logos | **Source Material Sidebar**: Shows exactly what documents the AI is referencing to kill "hallucination fear." |

| **HyperWrite** | [hyperwriteai.com](https://www.hyperwriteai.com/) | "AI-powered Grant Application Assistant." | Modern AI backend; Grant writer testimonials. | **Template Libraries**: Pre-built responses for common grant sections. |

---

## 🇪🇺 NL/EU Market Deep-Dive (NWO, ERC, MSCA)

Insights from specialized consultancies and regulatory bodies.

| Competitor / Entity | Market Focus | Key Insight | Lesson for PeerLens |
|---------------------|--------------|-------------|---------------------|
| **Yellow Research** | [NL/EU Consultant] | They create separate, high-trust landing pages for **ERC**, **MSCA**, and **NWO** services. | **Trust through Specificity**: Don't just say "EU Grants"; create dedicated rubric-modes for NWO vs ERC. |
| **NWO / EU Policy** | [Regulator] | They permit AI for **applicants** (editing/brainstorming) but prohibit it for **official reviewers**. | **Positioning**: Frame PeerLens as the **"Applicant's Pre-Reviewer"** — a safe, internal check before human submission. |
| **PNO / Hezelburcht** | [NL Consultants] | Dominate through manual expertise and high-touch consulting. | **The Speed Win**: Disrupt the manual €5k+ consulting model with instant €50 AI-rubric reviews. |
| **Enspire Science** | [EU Specialist] | Focuses heavily on the "Excellence" and "Impact" criteria of ERC. | **Criterion Focusing**: Deep-dive into European-specific definitions of "Impact" (Horizon Europe). |

---

## 🇳🇱 Strategic Wins for EU/NL Market (The PeerLens Edge)

While direct competitors focus on US (NIH/NSF) or general grants, PeerLens wins on **geospecific rubric compliance**.

| Opportunity Gap | Competitor State | PeerLens Strategy |
|-----------------|------------------|-------------------|
| **NL-Specific Rubrics** | None have NWO (Veni/Vedi/Vici) templates. | **Automated NWO Rubrics**: Pre-load NWO evaluation criteria as constraints. |
| **EU Frameworks** | Generic support at best. | **ERC/MSCA Specialists**: Deep grounding in Horizon Europe structures (Excellence, Impact, Implementation). |
| **Review over Writing** | Most focus on "Generating" text. | **"Expert Second Pair of Eyes"**: Position solely as a high-fidelity review tool for existing drafts. |
| **Compliance Proof** | Narrative claims of compliance. | **Visual Compliance Score**: Real-time 0-100 score based *strictly* on NWO/EU rubric points. |
| **Regulatory Safety** | Generic AI tools ignore policies. | **"The Pre-Reviewer"**: Explicitly market as a tool for researchers to use *before* the human committee sees it. |

---

## 🛠️ Analog Competitors (The "Gold Standard" for Academics)

These tools have perfected the art of selling AI to skeptical researchers.

| Competitor | URL | Hook / Value Prop | Trust Strategy | Top Lesson |
|---|---|---|---|---|
| **Writefull** | [writefull.com](https://www.writefull.com/) | "Academic writing is hard." | PhD testimonials from Ivy League / major labs | **The Pain Hook**: Start by acknowledging how hard the generic process is. |
| **Paperpal** | [paperpal.com](https://paperpal.com/) | "AI that brings out the best in you." | "Trusted by 4M+ academics," 1500+ journals | **Feature Tabs**: Categorized use cases with live demos. |
| **Overleaf** | [overleaf.com](https://www.overleaf.com/) | "Write like a rocket scientist." | ORCID login + Publisher logos (Nature, IEEE) | **Ecosystem Integration**: Use ORCID to signal authenticity. |
| **SciSpace** | [typeset.io](https://typeset.io/) | "Citation-backed results." | Focus on "280M+ papers" database | **Evidence First**: Researchers fear AI hallucinations; prove grounding. |
| **Elicit** | [elicit.com](https://elicit.com/) | "10x more evidence-based." | Massive user scale (5M+) + Corporate R&D logos | **Value Transformation**: Focus on being "evidence-based," not just "fast." |
| **Grammarly** | [grammarly.com](https://www.grammarly.com/) | "You think big. We’ll take care of the details." | Universal enterprise trust | **Empowerment**: Frame AI as an assistant that frees up the user's mind. |

---

## 📱 Internal App Interface (UX)

Patterns for the logged-in experience, dashboards, and review pages.

| Feature | Best-in-Class Pattern | Source | Lesson for PeerLens |
|---------|-----------------------|--------|---------------------|
| **Review UI** | Right-sidebar cards with categorized, actionable "Accept/Reject" suggestions. | Paperpal / Grammarly | Link reviews directly to rubrics; show feedback in categorized cards. |
| **Scoring** | Prominent 0-100 "Readiness Score" or "Language Quality" circular progress bar. | Grammarly / Paperpal | Use a "Grant Readiness Score" to gamify and show status. |
| **Dashboards** | Grid view with document previews, word counts, and "Last edited" timestamps. | Grammarly | Keep the dashboard clean; show review status (e.g., "Review Pending" vs "Complete"). |
| **Workspaces** | Tabular view for comparing multiple documents or metrics across papers. | SciSpace | For comparing multiple grant draft versions or rubrics side-by-side. |
| **Empty State** | Lead with onboarding templates ("Start with an NIH R01 Template"). | Paperpal | Don't show a blank page; show "Start from Template" CTAs. |
| **Contextual Tools** | Floating inline menus (Explain/Summarize) triggered by text selection. | SciSpace | Allow users to select a snippet and ask "Why is this weak?" in place. |

---

## 💡 Strategic Recommendations for PeerLens

Based on these 8 competitors, here is how we should differentiate:

### 1. The "Academic" Trust Stack
- **Recommendation**: Implement **ORCID Login** early. 
- **Why**: Overleaf used this to become the standard. It proves the tool is for *academics*, not just "general users."
- **Social Proof**: Instead of generic testimonials, use researcher roles (e.g., "Postdoc, Stanford", "Principal Investigator, Yale").

### 2. Addressing the "Hallucination" Fear
- **Recommendation**: Frame the review as "Rubric-Grounded" or "Evidence-Backed."
- **Why**: SciSpace and Elicit lead with "citation-backed" and "evidence-based" to solve the primary fear researchers have of LLMs.

### 3. Messaging: Partnership, not Replacement
- **Recommendation**: Adopt Grammarly/Paperpal's tone: "Focus on the science, we'll handle the rubric constraints."
- **Why**: Researchers take pride in their work. Frame the tool as a coach that "brings out your best" rather than a tool that "writes for you."

### 4. Layout: The Workflow Guide
- **Recommendation**: Use the **Tabbed Workflow** approach (Paperpal/Grantable). 
- **Sections**: 1. Draft Proposal → 2. Select Rubric → 3. Get Expert Review.

### 5. Multi-Page Gamification (App UX)
- **Recommendation**: Implement a **"Grant Readiness Score (0-100)"** in the top-right of the review page.
- **Why**: Grammarly and Paperpal use this to provide immediate orientation and drive the "completion" instinct.
- **Dashboard**: Show the word count and "Readiness Score" on the document cards in the user's dashboard.

### 6. Minimizing Blank-Page Friction
- **Recommendation**: Use **"Smart Templates"** in the empty dashboard state.
- **Example**: "Start with an NIH R01 draft structure" or "Paste your NSF Project Summary here."

### 7. The "Review-First" Differentiator
- **Recommendation**: Frame the UX around **"Upload Draft → Select Funder Rubric → Get 15-Min Review."**
- **Why**: Grantease already uses the "15-minute review" hook; PeerLens should own this for the EU/NL academic market.

---

## Source Artifacts
- Research performed: 2026-02-14
- Screenshots and session logs: `~/.gemini/antigravity/brain/2cfa0227-d562-41fe-af56-51493bab9394/`
