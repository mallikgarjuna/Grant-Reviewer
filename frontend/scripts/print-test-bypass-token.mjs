// frontend/scripts/print-test-bypass-token.mjs
import crypto from "node:crypto";

const version = "v1";
const userId = process.argv[2] ?? "agentic_test_user";
const timestamp = Math.floor(Date.now() / 1000);
const secret = process.env.TEST_AUTH_SECRET?.trim() ?? "";

if (!secret) {
  console.error("Missing TEST_AUTH_SECRET.");
  process.exit(1);
}
if (!/^[A-Za-z0-9:_-]{1,128}$/.test(userId)) {
  console.error("Invalid user id. Allowed pattern: [A-Za-z0-9:_-]{1,128}");
  process.exit(1);
}

const payload = `${version}.${userId}.${timestamp}`;
const signature = crypto
  .createHmac("sha256", secret)
  .update(payload)
  .digest("base64url");
const token = `${payload}.${signature}`;

console.log(`TOKEN=${token}`);
console.log(`COOKIE=gr_test_auth=${encodeURIComponent(token)}`);
