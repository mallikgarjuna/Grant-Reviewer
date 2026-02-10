import { createHash, createHmac } from "node:crypto";

/**
 * @param {string} text
 * @returns {string}
 */
export function normalizeSnippetText(text) {
  return text.replace(/\r\n/g, "\n").trim();
}

/**
 * @param {unknown} value
 * @returns {string}
 */
export function stableJsonStringify(value) {
  if (value === null) {
    return "null";
  }
  if (typeof value === "number" || typeof value === "boolean") {
    return JSON.stringify(value);
  }
  if (typeof value === "string") {
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) {
    return `[${value.map((entry) => stableJsonStringify(entry)).join(",")}]`;
  }
  if (typeof value === "object") {
    const entries = Object.entries(value)
      .filter(([, nested]) => nested !== undefined)
      .sort(([left], [right]) => left.localeCompare(right));
    const formatted = entries.map(
      ([key, nested]) => `${JSON.stringify(key)}:${stableJsonStringify(nested)}`,
    );
    return `{${formatted.join(",")}}`;
  }
  return "null";
}

/**
 * @param {string} text
 * @returns {string}
 */
export function sha256HexFromText(text) {
  return createHash("sha256").update(text, "utf8").digest("hex");
}

/**
 * @param {Uint8Array} bytes
 * @returns {string}
 */
export function sha256HexFromBytes(bytes) {
  return createHash("sha256").update(bytes).digest("hex");
}

/**
 * @param {object} params
 * @param {string} params.userId
 * @param {number} params.timestamp
 * @param {Uint8Array} params.bodyBytes
 * @returns {string}
 */
export function buildSignaturePayload({ userId, timestamp, bodyBytes }) {
  return `${userId}.${timestamp}.${sha256HexFromBytes(bodyBytes)}`;
}

/**
 * @param {string} secret
 * @param {string} payload
 * @returns {string}
 */
export function signSignaturePayload(secret, payload) {
  return createHmac("sha256", secret).update(payload, "utf8").digest("hex");
}
