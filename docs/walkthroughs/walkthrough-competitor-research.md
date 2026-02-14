# Walkthrough — Competitor Research for PeerLens

I have completed a comprehensive competitor research phase to inform the redesign of the PeerLens landing page. This research focused on understanding how successful academic and grant-specific tools build trust and convert skeptical researchers.

## Research Scope

I analyzed **8 competitors** across two categories:

### 1. Direct Competitors (AI + Grant Proposals)
- **Grantease**: Targeting NIH/Scientific grants with high university logos (Stanford, Duke).
- **Grantable**: Focusing on Nonprofits with a clear workflow-based layout.

### 2. Analog Competitors (The Academic "Gold Standard")
- **Writefull**: Mastery of "The Pain Hook" ("Academic writing is hard").
- **Paperpal**: Excellent use of feature tabs and live demos.
- **Overleaf**: Strategic use of ORCID login and publisher logos (Nature, IEEE).
- **SciSpace & Elicit**: Addressing the "hallucination fear" with citation-backed and evidence-based framing.
- **Grammarly**: Positioning AI as an empowering partner ("You think big").

## Key Deliverables

- **Inspiration Reference**: [inspiration.md](file:///home/mgurram/Projects/Github/AIEng_MG/Grant-Reviewer/docs/reference/inspiration.md) — The core synthesis of findings and recommendations.
- **Strategic Recommendations**: Detailed in the reference file, focusing on the "Academic Trust Stack," addressing hallucination fears, workflow-based layouts, and **100-point Grant Readiness Scores**.

## Internal App UX Research (Multi-Page Expansion)

I extended the research to cover the *logged-in* experience to support the building of document dashboards and review pages:
- **Review UI**: Identified the "Sidebar Card" pattern as the standard for AI feedback (Paperpal/Grammarly).
- **Gamification**: Recommended a **0-100 Readiness Score** to drive clarity and completion.
- **Onboarding**: Recommended **Smart Templates** for the empty dashboard state to reduce blank-page friction.

![App UX Research Session](file:///home/mgurram/Projects/Github/AIEng_MG/Grant-Reviewer/docs/walkthroughs/media/app_ux_patterns_research.webp)

- **Empty State**: Recommended **Smart Templates** for the empty dashboard state to reduce blank-page friction.

## Direct Competitor Deep-Dive: Grantable & Grantease

I performed a targeted deep-dive into the two most relevant direct competitors to identify PeerLens's unique "Strategic Win" in the EU/NL market:
- **Grantable**: Uses a **Source Material Sidebar** to ground AI suggestions. Primarily focused on general grant writing.
- **Grantease**: Tailored for **Scientific Research (NIH/NSF)**. It identifies RFA compliance requirements from text and frames the review as a "15-minute" task.
- **EU/NL Gap**: Verified that both leading tools have **zero built-in support** for NWO (NL) or ERC/MSCA (EU) specific rubrics.

![Direct Competitor Deep-Dive](file:///home/mgurram/Projects/Github/AIEng_MG/Grant-Reviewer/docs/walkthroughs/media/grant_competitor_deep_dive.webp)

| Feature | Competitor Inspiration | Lesson for PeerLens |
|---------|------------------------|---------------------|
| AI Instruction | Grantable's "Tell AI how to improve" | Allow users to refine reviews with rubric-laden prompts. |
| Compliance | Grantease's "Instance RFA Check" | Automate NWO/ERC rubric compliance—this is the PeerLens competitive edge. |

## NL/EU Market Research & Strategic Positioning

I performed a final research round focused on the Netherlands (NWO) and European (ERC/MSCA) funding landscape:
- **Regulatory Edge**: Discovered that NWO/EU officially permit AI for **applicants** but prohibit it for **reviewers**. This leads to the strategic positioning of PeerLens as a **"Safe Pre-Reviewer"** for researchers.
- **Manual vs. AI**: Identified that local incumbents (Yellow Research, Hezelburcht) rely on high-touch, expensive manual services. PeerLens disrupts this with instant, low-cost AI rubric reviews.
- **Specific Grounding**: Recommended creating dedicated rubric-modes for **NWO Veni/Vidi/Vici** and **Horizon Europe (ERC/MSCA)** to gain trust through geospecific expertise.

![NL/EU Research Session](file:///home/mgurram/Projects/Github/AIEng_MG/Grant-Reviewer/docs/walkthroughs/media/nl_eu_competitor_research.webp)

## Visual Evidence

The research was performed using an agentic browser. You can view the full recording of the session here:

![Competitor Research Session](file:///home/mgurram/Projects/Github/AIEng_MG/Grant-Reviewer/docs/walkthroughs/media/competitor_research_resume.webp)

---

## Next Steps

1. **Phase 0.2**: Revise the existing landing page brainstorm (@[docs/brainstorms/brainstorm-WF-0009-peerlens-landing-page.md]) using the new insights in `inspiration.md`.
2. **Phase 1.1**: Generate the landing page spec incorporating the "Academic Trust Stack" (e.g., ORCID login, PI/Researcher-led testimonials).
