# Frontend

Grant Reviewer frontend (Next.js App Router). This app is the product boundary (BFF): the browser calls same-origin `/api/bff/*`, and Next server routes call the FastAPI backend.

## WF-0009 Highlights

- Public marketing landing page on `/` for **PeerLens**
- New `/privacy` page with MVP privacy/retention statements
- Static demo tabs for `NWO Veni`, `ERC Starting`, and `MSCA PF`
- Review detail actions:
  - `Copy as text`
  - `Download .txt`
  - `Delete review` (through BFF `DELETE /api/bff/reviews/[reviewId]`)

## Key Routes

- `/` — PeerLens landing page
- `/privacy` — privacy statements
- `/sign-in` — authentication entry
- `/app` — authenticated submission page
- `/app/reviews/[reviewId]` — review detail, export, and delete

## Getting Started

### Prerequisites

- Node.js `22.17.0` (pinned in repo `.nvmrc`)
- If you use `nvm`: `nvm use`
- Clerk application keys
- Backend API running (FastAPI), with matching `BFF_SHARED_SECRET`

### Install

```bash
source ~/.nvm/nvm.sh
nvm use

npm install
cp .env.local.example .env.local
```

Edit `.env.local`:
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
- `CLERK_SECRET_KEY`
- `FASTAPI_BASE_URL` (server-only)
- `BFF_SHARED_SECRET` (must match backend)

### Dev

```bash
npm run dev
```

Open `http://localhost:3000`.

## Verification

```bash
npm run lint
npm run check:bff
npm run check:seo
```

Notes:
- `check:bff` validates payload normalization + signing invariants.
- `check:seo` validates `/app/*` noindex + robots disallow guardrails (static check by default).

Manual checks for WF-0009:
- Landing `/` renders required sections and CTA links.
- `/privacy` includes retention/deletion/training statements.
- Signed-in review page supports copy, `.txt` download, and delete.

End-to-end local verification helper from repo root:

```bash
bash scripts/verify_local_8_0A.sh
```

## Deploy

Vercel is the intended hosting target (Task `8.0C` wires deployment + secrets).
