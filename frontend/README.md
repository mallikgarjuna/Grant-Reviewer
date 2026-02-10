Grant Reviewer frontend (Next.js App Router). This app is the product boundary (BFF): the browser calls same-origin `/api/bff/*`, and Next server routes call the FastAPI backend.

## Getting Started

### Prerequisites

- Node.js `22.17.0`
- If you use `nvm`: `nvm use v22.17.0`
- Clerk application keys

### Install

```bash
source ~/.nvm/nvm.sh
nvm use v22.17.0

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

### Verification

```bash
npm run lint
npm run check:bff
npm run check:seo
```

End-to-end local verification (including manual browser checklist) is orchestrated from repo root:

```bash
bash scripts/verify_local_8_0A.sh
```

Notes:
- `check:bff` validates payload normalization + signing invariants.
- `check:seo` validates `/app/*` noindex + robots disallow guardrails (static check by default).

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy

Vercel is the intended hosting target (Task `8.0C` wires deployment + secrets).

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
