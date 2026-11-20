// news-image-20261120 entry (Node 22, standard library only).
// The image is entry.png beside this file, drawn at build time from the
// verified news of Friday 20 November 2026. All this program does is copy
// it to /output/entry.png, where the gate reads it and the judge sees it.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, statSync } from 'node:fs';
import { join } from 'node:path';

const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const MAX_BYTES = 1048576; // the gate refuses any image over 1 MiB

const entryPath = new URL('./entry.png', import.meta.url);
let size;
try {
  size = statSync(entryPath).size;
} catch {
  throw new Error('entry.png is missing from the repository root');
}
if (size > MAX_BYTES) {
  throw new Error(`entry.png is ${size} bytes, over the 1 MiB cap`);
}

copyFileSync(entryPath, join(OUTPUT_DIR, 'entry.png'));
