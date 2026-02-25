#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "== Task 8.0A Local Verification =="
echo "Purpose: run reproducible checks that cannot run reliably in the Codex sandbox."
echo "Why: sandbox cannot bind web ports consistently, so runtime auth/app flow must be verified on your machine."
echo

if [[ -s "${NVM_DIR:-$HOME/.nvm}/nvm.sh" ]]; then
  # shellcheck disable=SC1090
  source "${NVM_DIR:-$HOME/.nvm}/nvm.sh"
  nvm use >/dev/null
fi

echo "Node: $(node -v)"
echo "npm:  $(npm -v)"
echo

echo "[1/3] Frontend static + contract checks"
(
  cd frontend
  npm run check:bff
  npm run check:seo
  npm run lint
)
echo

echo "[2/3] Backend API smoke check (stub mode, signed BFF flow)"
if command -v uv >/dev/null 2>&1; then
  (
    cd backend
    UV_CACHE_DIR="$PWD/.uv-cache" \
    PYTHONPATH=. \
    BFF_SHARED_SECRET="${BFF_SHARED_SECRET:-dev}" \
    LLM_MODE=stub \
    uv run python - <<'PY'
import hashlib
import hmac
import json
import os
import time

from fastapi.testclient import TestClient
from main import app

secret = os.environ.get("BFF_SHARED_SECRET", "dev")
user = "local-user"
client = TestClient(app)

def signed_headers(body: bytes = b"") -> dict[str, str]:
    timestamp = str(int(time.time()))
    payload = f"{user}.{timestamp}.{hashlib.sha256(body).hexdigest()}"
    signature = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return {
        "X-GR-User-Id": user,
        "X-GR-Timestamp": timestamp,
        "X-GR-Signature": signature,
    }

calls = client.get("/calls", headers=signed_headers())
print("calls_status", calls.status_code)
call_id = calls.json()["calls"][0]["id"]

nodes = client.get(f"/calls/{call_id}/nodes", headers=signed_headers())
print("nodes_status", nodes.status_code)
node_id = next(n["id"] for n in nodes.json()["nodes"] if n["has_expectations"])

body = json.dumps(
    {"call_id": call_id, "node_id": node_id, "snippet_text": "local verify text"}
).encode()
idempotency_key = f"verify-8-0a-{int(time.time())}"
create = client.post(
    "/reviews",
    data=body,
    headers={
        **signed_headers(body),
        "Content-Type": "application/json",
        "Idempotency-Key": idempotency_key,
    },
)
print("create_status", create.status_code, create.json().get("status"))
review_id = create.json()["review_id"]

detail = client.get(f"/reviews/{review_id}", headers=signed_headers())
print("detail_status", detail.status_code, "cards", len(detail.json().get("cards", [])))
PY
  )
else
  echo "ERROR: 'uv' is required for backend smoke verification."
  exit 1
fi
echo

echo "[3/3] Manual browser checklist (required to close 8.0A.12)"
cat <<'EOF'
Run these in separate terminals:

  Terminal A (backend):
    cd backend
    BFF_SHARED_SECRET=<same-as-frontend> LLM_MODE=stub uv run uvicorn main:app --reload

  Terminal B (frontend):
    cd frontend
    npm run dev

Then verify in browser:
  [ ] /blog is public
  [ ] /app redirects to /sign-in when signed out
  [ ] Sign in succeeds and returns to /app
  [ ] Submit review from /app and reach /app/reviews/[id]
  [ ] Refresh/re-submit unchanged draft (idempotent behavior)
  [ ] FAILED retry creates a new attempt key
  [ ] Deep link /app/reviews/[id] works after auth

Important:
  - frontend/.env.local BFF_SHARED_SECRET must match backend/.env (or backend startup env)
  - this script proves static + API contract health, while manual browser steps validate UX/auth routing
EOF

echo
echo "Done: automated checks passed. Complete the manual checklist above to close Task 8.0A.12."
