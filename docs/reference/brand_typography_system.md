# PeerLens — Typography System (Serif + Sans Architecture)

Reference during UI implementation and component design.

This file extends:
@docs/reference/brand_guidelines.md

Brand file defines tone.
This file defines implementation structure.

---

# 1. Font Architecture

Authority Layer (Editorial / Academic)

- Lora
- Used for major headings only

System Layer (UI / Interaction / Body)

- Inter
- Used for everything else

Principle:
Serif = authority
Sans-serif = clarity
Use serif only for primary large headings and editorial titles.
Never mix serif + sans in the same sentence.

---

# 2. Font Loading (Next.js)

Use next/font/google:

Lora:
weights: 600
CSS var: --font-heading

Inter:
weights: 400, 500, 600
CSS var: --font-body

Attach both variables to <html>.

Tailwind config:
fontFamily: {
heading: ['var(--font-heading)'],
body: ['var(--font-body)'],
}

---

# 3. Usage Rules

## Marketing Pages

H1 → Lora 600
H2 → Lora 600
H3 → Lora 600
Body → Inter 400
Buttons/Nav → Inter 500–600

---

## App Interface (/app/\*)

Page Title (editorial/marketing) → Lora 600
Section Title (editorial) → Lora 600
Section Title (dense UI) → Inter 600
Body Text → Inter 400
Forms / Inputs / Tables → Inter only

Never use serif inside:

- Forms
- Tables
- Buttons
- Dense UI

---

## Review Cards (Core Feature)

Card Title → Inter 600 (unless explicitly editorial)
Feedback Text → Inter 400
Scores / Tags → Inter 600

Do NOT use serif for long paragraphs or dense UI card text.

---

# 4. Typographic Scale

H1 (editorial):
clamp(2.2rem, 3.6vw, 2.95rem)
line-height: 1.22
weight: 600

H2 (editorial):
clamp(1.55rem, 2.1vw, 1.95rem)
line-height: 1.28
weight: 600

H3:
clamp(1.2rem, 1.45vw, 1.32rem)
line-height: 1.36
weight: 600

Body:
16px
line-height: 1.6

Small:
14px

Micro:
12px

---

# 5. Letter Spacing

Lora headings:
very light negative tracking (-0.01em max)

Inter body:
default tracking

No decorative tracking.

---

# 6. Readability Constraints (Non-Negotiable)

- Max text width: 672px
- Never justify text
- Never drop body below 16px
- Minimum 24px vertical spacing between content blocks
- No center-aligned paragraphs except hero sections

Researchers read dense text.
Clarity > aesthetics.

---

# 7. Weight Discipline

Allowed:

- Inter: 400 / 500 / 600
- Lora: 600

Avoid:

- Excessive bold
- 800+ weights
- Mixing serif + sans in one sentence

---

# 8. Design Intent

PeerLens must feel:

- Scholarly
- Calm
- Structured
- Thoughtful
- Not startup-hype

Typography should communicate quiet authority.

If it looks decorative, reduce it.
If it looks loud, soften it.

---

END OF FILE
