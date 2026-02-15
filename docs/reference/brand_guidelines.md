# PeerLens — Brand Guidelines

Reference this file during brainstorming, spec, or implementation with:
`@docs/reference/brand_guidelines.md`

Do NOT modify this file during execution — update via a dedicated WF.

---

## Brand Identity

| Property | Value |
|----------|-------|
| **Product Name** | PeerLens |
| **Tagline** | Sharpen your proposal before you submit |
| **Logo** | Text-only wordmark — "PeerLens" in Inter Bold |
| **Voice & Tone** | Friendly expert — warm, clear, jargon-aware but not dumbed down. Like a helpful postdoc. |

### Voice Examples

| ✅ Do | ❌ Don't |
|-------|---------|
| "We found 3 areas that could be stronger" | "ALERT: 3 critical issues detected" |
| "Your methods section aligns well with the evaluation criteria" | "Congrats! You nailed it! 🎉" |
| "This section could benefit from more specificity" | "Insufficient detail provided" |

---

## Color Palette

### Core Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `--primary` | `#2563EB` | Primary actions, links, focus rings |
| `--primary-foreground` | `#FFFFFF` | Text on primary backgrounds |
| `--foreground` | `#0F172A` | Body text, headings (slate-900) |
| `--background` | `#FFFFFF` | Page background |
| `--surface` | `#F8FAFC` | Cards, elevated surfaces (slate-50) |
| `--surface-muted` | `#F1F5F9` | Secondary surfaces, hover states (slate-100) |
| `--border` | `#CBD5E1` | Borders, dividers (slate-300) |
| `--muted-foreground` | `#64748B` | Secondary text, captions (slate-500) |

### Accent Color

| Token | Hex | Usage |
|-------|-----|-------|
| `--accent` | `#0D9488` | Badges, highlights, tags, secondary actions (teal-600) |
| `--accent-foreground` | `#FFFFFF` | Text on accent backgrounds |

### Semantic Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `--success` | `#059669` | Positive feedback, "strong" indicators (emerald-600) |
| `--warning` | `#D97706` | Caution, "needs attention" indicators (amber-600) |
| `--error` | `#DC2626` | Errors, validation failures (red-600) |

### Color Principles

- **Restrained usage** — most of the page should be white/slate. Color draws attention to what matters.
- **No harsh reds** in feedback — use amber for "needs improvement", reserve red for form errors only.
- **Blue = action** — if it's blue, you can click it.

---

## Typography

### Font

| Property | Value |
|----------|-------|
| **Family** | [Inter](https://rsms.me/inter/) (headings + body) |
| **Fallback** | `-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif` |
| **CSS Variable** | `var(--font-inter)` |

### Weight Hierarchy (Restrained)

Deliberately lighter than typical SaaS — scholarly, approachable, non-salesy.

| Element | Weight | Size | Line Height |
|---------|--------|------|-------------|
| **H1** | `600` (semibold) | `clamp(2rem, 4vw, 3rem)` | `1.1` |
| **H2** | `500` (medium) | `clamp(1.5rem, 2.8vw, 2.25rem)` | `1.2` |
| **H3** | `500` (medium) | `clamp(1.25rem, 2vw, 1.5rem)` | `1.3` |
| **Body** | `400` (regular) | `1rem` (16px) | `1.5` |
| **Small / Caption** | `400` (regular) | `0.875rem` (14px) | `1.4` |
| **Eyebrow** | `600` (semibold) | `0.75rem` (12px), uppercase, `tracking-[0.2em]` | `1.5` |

### Typography Principles

- **Letter-spacing**: `-0.02em` on all headings for tightness.
- **No bold body text** in long-form — use semibold sparingly for emphasis.
- **Monospace** (`font-mono`) for review IDs, technical values only.

---

## Spacing & Layout

### Spacing Scale (Airy)

Design for generous whitespace — feels calm, premium, academic-friendly.

| Token | Value | Usage |
|-------|-------|-------|
| `xs` | `4px` | Tight gaps (icon-to-text) |
| `sm` | `8px` | Inner padding, small gaps |
| `md` | `16px` | Default component padding |
| `lg` | `24px` | Section inner padding |
| `xl` | `32px` | Between components |
| `2xl` | `48px` | Between page sections |
| `3xl` | `64px` | Major section breaks |
| `4xl` | `96px` | Hero-level vertical padding |

### Layout Principles

- **Max content width**: `672px` for text-heavy content (readability).
- **Max page width**: `1200px` for full layouts.
- **Section padding**: Minimum `48px` vertical between major sections.
- **Cards**: `24px` inner padding, `1px` border, `var(--radius-md)` corners.
- **Let content breathe** — when in doubt, add more whitespace.

---

## Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `--radius-sm` | `8px` | Small elements (badges, tags) |
| `--radius-md` | `12px` | Buttons, inputs, cards |
| `--radius-lg` | `16px` | Large containers, modals |
| `--radius-full` | `9999px` | Avatars, pills |

---

## Imagery & Icons

### Imagery

- **MVP**: Clean text + product screenshots only. No illustrations.
- **Screenshots**: Use real product UI, lightly styled with border + shadow.
- **Photography**: Avoid stock photos. If needed later, use authentic academic settings.

### Icons

- **Library**: [Lucide](https://lucide.dev/) — clean, thin, consistent.
- **Size**: `20px` inline with text, `24px` standalone.
- **Stroke**: `1.5px` (Lucide default) — pairs well with Inter's clean lines.
- **Color**: Inherit from text color (`currentColor`).

---

## Interaction Principles

1. **Clarity over cleverness** — each screen answers "what do I do next?"
2. **Trust and calm** — neutral surfaces, minimal shadows, restrained color.
3. **Speed feel** — snappy hover/press states, short micro-animations (`150ms–200ms`).
4. **One primary action per screen** — secondary/tertiary actions visually de-emphasized.
5. **Accessible by default** — visible focus rings (`3px solid #2563EB`), reduced-motion support.

### Hover & Focus States

| State | Style |
|-------|-------|
| **Hover** (buttons) | `brightness(1.05)` or subtle background shift |
| **Hover** (links) | Underline on hover |
| **Focus-visible** | `outline: 3px solid #2563EB; outline-offset: 2px` |
| **Disabled** | `opacity: 0.6; cursor: not-allowed` |

---

## Accessibility (MVP Baseline)

- **WCAG AA** contrast targets for all text and controls.
- Form inputs have visible labels (or accessible names).
- Buttons/inputs are keyboard reachable with visible focus.
- Error messages are associated to inputs.
- Reduced-motion support via `prefers-reduced-motion`.

---

## Theme

| Property | Value |
|----------|-------|
| **Mode** | Light-only (MVP) |
| **Background pattern** | Subtle 32px grid lines (`rgba(15,23,42, 0.04)`) |

Dark mode is explicitly deferred.

---

## Quick Copy-Paste (CSS Variables)

```css
:root {
  --background: #ffffff;
  --foreground: #0f172a;
  --surface: #f8fafc;
  --surface-muted: #f1f5f9;
  --border: #cbd5e1;
  --muted-foreground: #64748b;
  --primary: #2563eb;
  --primary-foreground: #ffffff;
  --accent: #0d9488;
  --accent-foreground: #ffffff;
  --success: #059669;
  --warning: #d97706;
  --error: #dc2626;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-full: 9999px;
}
```
