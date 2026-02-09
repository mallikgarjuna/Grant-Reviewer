import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const projectRoot = process.cwd();

function assertStaticConfig() {
  const robotsFile = path.join(projectRoot, "src", "app", "robots.ts");
  const robotsSource = fs.readFileSync(robotsFile, "utf8");
  assert(
    robotsSource.includes('disallow: ["/app/"]'),
    "robots.ts must disallow /app/.",
  );

  const nextConfigFile = path.join(projectRoot, "next.config.ts");
  const nextConfigSource = fs.readFileSync(nextConfigFile, "utf8");
  assert(
    nextConfigSource.includes('source: "/app/:path*"'),
    "next.config.ts must target /app/:path* for headers.",
  );
  assert(
    nextConfigSource.includes('key: "X-Robots-Tag"') &&
      nextConfigSource.includes('value: "noindex"'),
    "next.config.ts must set X-Robots-Tag: noindex.",
  );
}

async function assertRuntimeHeaders(baseUrl) {
  const robotsResponse = await fetch(`${baseUrl}/robots.txt`, {
    redirect: "manual",
  });
  const robotsTxt = await robotsResponse.text();
  assert(
    robotsTxt.includes("Disallow: /app/"),
    "robots.txt runtime output must include Disallow: /app/.",
  );

  const appResponse = await fetch(`${baseUrl}/app`, {
    redirect: "manual",
  });
  const robotsTag = appResponse.headers.get("x-robots-tag");
  assert.equal(
    robotsTag,
    "noindex",
    "runtime /app response must include X-Robots-Tag: noindex.",
  );
}

async function main() {
  assertStaticConfig();
  const runtimeBaseUrl = process.env.SEO_CHECK_BASE_URL?.trim();
  if (runtimeBaseUrl) {
    await assertRuntimeHeaders(runtimeBaseUrl);
    process.stdout.write(`seo-guardrail-check: ok (static + runtime: ${runtimeBaseUrl})\n`);
    return;
  }
  process.stdout.write("seo-guardrail-check: ok (static)\n");
}

try {
  await main();
} catch (error) {
  process.stderr.write(
    `seo-guardrail-check: failed: ${error instanceof Error ? error.message : String(error)}\n`,
  );
  process.exit(1);
}
