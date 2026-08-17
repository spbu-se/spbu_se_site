// Regenerates the production quick-website css/js from the committed sources:
//   src/static/assets/js/quick-website.js   -> quick-website.min.js  (terser)
//   src/static/assets/css/quick-website.css -> quick-website.min.css (purgecss + esbuild)
//
// The theme CSS is purged against the real content (templates + all JS under
// assets, including bundled libs) so only the rules the site can actually use
// survive; greedy safelist keeps class families that are built dynamically at
// runtime (JS string concatenation). Build-and-commit: run `npm run build`,
// commit both outputs with the source change. CI job `assets` re-runs this and
// fails if the committed outputs drift.

import { transform } from "esbuild";
import { minify } from "terser";
import { PurgeCSS } from "purgecss";
import { readFile, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const assets = path.join(root, "src", "static", "assets");

const cssIn = path.join(assets, "css", "quick-website.css");
const cssOut = path.join(assets, "css", "quick-website.min.css");
const jsIn = path.join(assets, "js", "quick-website.js");
const jsOut = path.join(assets, "js", "quick-website.min.js");

// Class families built dynamically in JS (string concatenation / data-toggle
// conventions) that a static content scan cannot see. Generic Bootstrap state
// classes (active, show, fade, btn-*, badge-*, ...) appear literally in the
// templates, so they are already kept by the content scan and need no greedy
// safelist entry.
const dynamicPrefixes = [
  "popover-", "swiper-", "select2-", "flatpickr-", "fc-", "hljs-",
  "countdown-", "scroll-", "ps-", "tagsinput-", "label-", "toast-",
  "tooltip-", "g-sidenav-", "sidenav-", "omnisearch-",
];

// Glob patterns need forward slashes even on Windows (purgecss uses `glob`).
const globSrc = (rel) => path.join(root, rel).replaceAll("\\", "/");

const escapeRegExp = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

const purged = await new PurgeCSS().purge({
  content: [
    globSrc("src/templates/**/*.html"),
    globSrc("src/static/assets/**/*.js"),
  ],
  css: [cssIn.replaceAll("\\", "/")],
  defaultExtractor: (content) => content.match(/[\w-/:]+(?<!:)/g) || [],
  // purgecss v7 greedy safelist accepts RegExp only (it calls `.test()`).
  safelist: { greedy: dynamicPrefixes.map((p) => new RegExp(escapeRegExp(p))) },
});
if (!purged.length || !purged[0].css) {
  throw new Error("purgecss produced no output for " + cssIn);
}

const purgedCss = purged[0].css;
const cssResult = await transform(purgedCss, { loader: "css", minify: true });
await writeFile(cssOut, cssResult.code, "utf8");

const js = await readFile(jsIn, "utf8");
const jsResult = await minify(js, { format: { comments: false } });
if (!jsResult.code) {
  throw new Error("terser produced no output for " + jsIn);
}
await writeFile(jsOut, jsResult.code, "utf8");

console.log("built " + path.relative(root, cssOut));
console.log("built " + path.relative(root, jsOut));
