import "server-only";

function readRequiredEnv(name: "FASTAPI_BASE_URL" | "BFF_SHARED_SECRET"): string {
  const value = process.env[name]?.trim();
  if (!value) {
    throw new Error(`Missing required server env var: ${name}`);
  }
  return value;
}

export function getFastApiBaseUrl(): string {
  return readRequiredEnv("FASTAPI_BASE_URL");
}

export function getBffSharedSecret(): string {
  return readRequiredEnv("BFF_SHARED_SECRET");
}
