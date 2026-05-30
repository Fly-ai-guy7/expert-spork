#!/usr/bin/env node
// Bundle budget gate. Fails CI if the gzipped initial JS exceeds the cap.
// Tier 1.2 plan target: 250 KB gz initial.
import { readdir, readFile } from "node:fs/promises";
import { gzipSync } from "node:zlib";
import { join } from "node:path";

const DIST = new URL("../dist/assets/", import.meta.url).pathname;
const LIMIT_BYTES = 250 * 1024;

const files = await readdir(DIST);
const js = files.filter((f) => f.endsWith(".js"));
if (js.length === 0) {
  console.error("no JS bundles in dist/assets — did you `npm run build`?");
  process.exit(1);
}

let totalRaw = 0;
let totalGz = 0;
for (const f of js) {
  const buf = await readFile(join(DIST, f));
  const gz = gzipSync(buf).length;
  totalRaw += buf.length;
  totalGz += gz;
  console.log(`${f}: ${(buf.length / 1024).toFixed(1)} KB raw · ${(gz / 1024).toFixed(1)} KB gz`);
}
console.log(`\ntotal: ${(totalRaw / 1024).toFixed(1)} KB raw · ${(totalGz / 1024).toFixed(1)} KB gz`);
console.log(`budget: ${(LIMIT_BYTES / 1024).toFixed(0)} KB gz`);

if (totalGz > LIMIT_BYTES) {
  console.error(`\nFAIL: gzipped JS ${(totalGz / 1024).toFixed(1)} KB exceeds budget`);
  process.exit(1);
}
console.log("OK");
