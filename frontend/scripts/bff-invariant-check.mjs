import assert from "node:assert/strict";

import {
  buildSignaturePayload,
  normalizeSnippetText,
  sha256HexFromText,
  signSignaturePayload,
  stableJsonStringify,
} from "../src/lib/bff/crypto-utils.mjs";

function run() {
  const draft = {
    call_id: "call-123",
    node_id: "node-456",
    snippet_text: "  First line.\r\nSecond line.\n",
  };

  const normalizedOnce = {
    ...draft,
    snippet_text: normalizeSnippetText(draft.snippet_text),
  };
  const normalizedTwice = {
    ...normalizedOnce,
    snippet_text: normalizeSnippetText(normalizedOnce.snippet_text),
  };

  const once = stableJsonStringify(normalizedOnce);
  const twice = stableJsonStringify(normalizedTwice);
  assert.equal(once, twice, "Normalization must be stable across repeated runs.");
  assert.equal(
    sha256HexFromText(once),
    sha256HexFromText(twice),
    "Payload hash must remain stable after repeated normalization.",
  );

  const secret = "dev-secret";
  const userId = "user-1";
  const timestamp = 1_700_000_000;

  const payloadA = buildSignaturePayload({
    userId,
    timestamp,
    bodyBytes: new TextEncoder().encode('{"a":1}'),
  });
  const payloadB = buildSignaturePayload({
    userId,
    timestamp,
    bodyBytes: new TextEncoder().encode('{"a":2}'),
  });
  const signatureA = signSignaturePayload(secret, payloadA);
  const signatureARepeat = signSignaturePayload(secret, payloadA);
  const signatureB = signSignaturePayload(secret, payloadB);

  assert.equal(
    signatureA,
    signatureARepeat,
    "Signature must be deterministic for identical bytes.",
  );
  assert.notEqual(
    signatureA,
    signatureB,
    "Signature must change when request body bytes change.",
  );

  process.stdout.write("bff-invariant-check: ok\n");
}

try {
  run();
} catch (error) {
  process.stderr.write(
    `bff-invariant-check: failed: ${error instanceof Error ? error.message : String(error)}\n`,
  );
  process.exit(1);
}
