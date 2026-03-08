// frontend/src/lib/auth/testBypassAuth.ts
const TEST_BYPASS_COOKIE_NAME = "gr_test_auth";
const TEST_BYPASS_HEADER_NAME = "x-gr-test-auth";
const TEST_BYPASS_TOKEN_VERSION = "v1";

export type AuthMode = "clerk" | "test_bypass";

function toUrlSafeBase64(bytes: Uint8Array): string {
  let binary = "";
  bytes.forEach((byte) => {
    binary += String.fromCharCode(byte);
  });
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}

function parseCookieValue(cookieHeader: string, key: string): string | null {
  const chunks = cookieHeader.split(";");
  for (const chunk of chunks) {
    const [rawName, ...rawValueParts] = chunk.trim().split("=");
    if (rawName !== key) {
      continue;
    }
    const joined = rawValueParts.join("=");
    if (!joined) {
      return null;
    }
    try {
      return decodeURIComponent(joined);
    } catch {
      return joined;
    }
  }
  return null;
}

function safeEqual(left: string, right: string): boolean {
  if (left.length !== right.length) {
    return false;
  }
  let mismatch = 0;
  for (let index = 0; index < left.length; index += 1) {
    mismatch |= left.charCodeAt(index) ^ right.charCodeAt(index);
  }
  return mismatch === 0;
}

function isValidBypassUserId(userId: string): boolean {
  return /^[A-Za-z0-9:_-]{1,128}$/.test(userId);
}

function getDefaultBypassUserId(): string | null {
  const candidate = process.env.TEST_AUTH_DEFAULT_USER_ID?.trim() ?? "";
  if (!candidate) {
    return null;
  }
  if (!isValidBypassUserId(candidate)) {
    return null;
  }
  return candidate;
}

function getBypassMaxAgeSeconds(): number {
  const configured = Number.parseInt(
    process.env.TEST_AUTH_MAX_AGE_SECONDS?.trim() ?? "",
    10,
  );
  if (!Number.isFinite(configured)) {
    return 3_600;
  }
  if (configured < 60) {
    return 60;
  }
  if (configured > 86_400) {
    return 86_400;
  }
  return configured;
}

async function signBypassPayload(secret: string, payload: string): Promise<string> {
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    {
      name: "HMAC",
      hash: "SHA-256",
    },
    false,
    ["sign"],
  );
  const signature = await crypto.subtle.sign(
    "HMAC",
    key,
    new TextEncoder().encode(payload),
  );
  return toUrlSafeBase64(new Uint8Array(signature));
}

function getBypassTokenFromRequest(request: Request): string | null {
  const headerValue = request.headers.get(TEST_BYPASS_HEADER_NAME)?.trim();
  if (headerValue) {
    return headerValue;
  }
  const cookieHeader = request.headers.get("cookie");
  if (!cookieHeader) {
    return null;
  }
  return parseCookieValue(cookieHeader, TEST_BYPASS_COOKIE_NAME);
}

export function getAuthMode(): AuthMode {
  const raw = process.env.AUTH_MODE?.trim().toLowerCase() ?? "clerk";
  if (raw === "test_bypass") {
    return "test_bypass";
  }
  return "clerk";
}

export function isTestBypassMode(): boolean {
  return getAuthMode() === "test_bypass";
}

export function getTestBypassConfigError(): string | null {
  if (!isTestBypassMode()) {
    return null;
  }
  if (process.env.NODE_ENV === "production") {
    return "TEST_BYPASS_FORBIDDEN_IN_PRODUCTION";
  }
  const secret = process.env.TEST_AUTH_SECRET?.trim() ?? "";
  if (!secret || secret.includes("REPLACE_ME")) {
    return "TEST_AUTH_SECRET_MISSING_OR_INVALID";
  }
  return null;
}

export async function resolveBypassUserId(request: Request): Promise<string | null> {
  if (!isTestBypassMode()) {
    return null;
  }
  if (getTestBypassConfigError() !== null) {
    return null;
  }

  const token = getBypassTokenFromRequest(request);
  if (!token) {
    return getDefaultBypassUserId();
  }

  const parts = token.split(".");
  if (parts.length !== 4) {
    return null;
  }
  const [version, userId, rawTimestamp, signature] = parts;
  if (version !== TEST_BYPASS_TOKEN_VERSION || !isValidBypassUserId(userId)) {
    return null;
  }
  const timestamp = Number.parseInt(rawTimestamp, 10);
  if (!Number.isFinite(timestamp) || timestamp <= 0) {
    return null;
  }
  const nowSeconds = Math.floor(Date.now() / 1000);
  const maxAgeSeconds = getBypassMaxAgeSeconds();
  if (Math.abs(nowSeconds - timestamp) > maxAgeSeconds) {
    return null;
  }

  const secret = process.env.TEST_AUTH_SECRET?.trim() ?? "";
  const payload = `${version}.${userId}.${timestamp}`;
  const expected = await signBypassPayload(secret, payload);
  if (!safeEqual(expected, signature)) {
    return null;
  }
  return userId;
}

export function resolveDefaultBypassUserId(): string | null {
  if (!isTestBypassMode()) {
    return null;
  }
  if (getTestBypassConfigError() !== null) {
    return null;
  }
  return getDefaultBypassUserId();
}

export async function buildTestBypassToken(
  userId: string,
  timestampSeconds: number = Math.floor(Date.now() / 1000),
): Promise<string> {
  const secret = process.env.TEST_AUTH_SECRET?.trim() ?? "";
  if (!secret) {
    throw new Error("TEST_AUTH_SECRET is required to build a bypass token.");
  }
  if (!isValidBypassUserId(userId)) {
    throw new Error("Invalid test bypass user id format.");
  }
  const payload = `${TEST_BYPASS_TOKEN_VERSION}.${userId}.${timestampSeconds}`;
  const signature = await signBypassPayload(secret, payload);
  return `${payload}.${signature}`;
}
