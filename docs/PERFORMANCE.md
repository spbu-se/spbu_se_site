# PERFORMANCE.md

<!-- encoding: utf-8 -->

Scope: performance optimization roadmap for se.math.spbu.ru — baseline
measurements, shipped Tier 1 work, and the deferred ideas/goals backlog.

Covers: performance baseline/measurements, shipped optimizations (Tier 1, Font
Awesome subset, app-side cache headers), deferred Tier 2/3 ideas, post-deploy
re-evaluation return-item. Does not cover: SEO/agentic roadmap — see
`docs/SEO_A11Y_ROADMAP.md`, general quality tiers — see
`docs/QUALITY_MANAGEMENT.md`.

## Baseline (measured 2026-08-15)

- Mobile Lighthouse Performance score: **63** (local run, `npx lighthouse`,
  homepage). Field metrics (CrUX, 28-day) are green on both devices — this
  backlog targets the lab score and transfer/cache hygiene.
- Homepage text assets ~**1.07 MB uncompressed** (no gzip/brotli on the host).
  Largest: `quick-website.css` 573 KB, `simplemde.min.js` 269 KB, `feather.min.js` 76 KB.
- All static assets served `Cache-Control: no-cache` (re-validated every visit).
- Google Maps API JS loaded synchronously on every page; SimpleMDE loaded on
  every `base_light` page (only ~6 pages render the editor).

## Post-gzip lab measurement (2026-08-17, pre-release)

Only the host nginx gzip was live (cache headers not yet applied; app-side Tier 1
not yet deployed): **mobile 67 / desktop 94** (PSI). Review the 67 after the next
release deploys Tier 1 + cache; do not extrapolate from this partial state.

## Shipped — Tier 1 (PR: perf-assets-tier1)

- 4 base templates: `preconnect`/`dns-prefetch` for GTM + topbar.spbu.ru;
  versioned static URLs via an `asset()` Jinja macro; `feather.min.js` deferred
  with the inline `feather.replace()` moved to a DOMContentLoaded listener.
- Asset version parametrized: a single `asset(path)` macro (defined in the 4
  bases, inherited by children) appends `?v=ASSET_VERSION`; the version is the
  deploy date (`flask_se_config.site_deploy_date()` ← `SE_SITE_LASTMOD`,
  default today) — same single source as the sitemap static lastmod. No literal
  version in any template, so nothing to bump per release.
- SimpleMDE removed from the `base_light` global; explicit include added to the
  two pages that depend on it (`practice/student/new_report.html`,
  `practice/staff/reports_staff.html`) with an XHR guard.
- Hero/card JPEGs recompressed (quality 72, progressive): mm.jpg, mm2.jpg,
  main-back.jpg, main2.jpg, campus-1/2/3.jpg, building-photo.jpg
  (~670 KB → ~200 KB).
- Host nginx gzip (verified live 2026-08-17). The immutable/30-day cache headers
  are set **app-side** (host nginx is a pure reverse proxy; static is served by
  Flask/uwsgi) — `after_request` in `flask_se.py` gives
  `/assets/{css,js,libs}/` → `public, max-age=31536000, immutable` and
  `/assets/img/` → `public, max-age=2592000` (shipped in `perf/fa-subset`).
  Safe because css/js/libs URLs carry the release-date `?v=`.
- Baseline Lighthouse JSON: `.tmp/baseline_lighthouse.json`.

## Post-release measurement (2026-08-17, v2026.08.17 live)

Return-item completed. Measured on the deployed release (local `npx lighthouse`,
homepage, mobile; 2 runs, stable):

- **Lab mobile Performance: 66** (baseline 63 → +3). The **>70 target is NOT met**
  by the lab score. Lab throttling (Slow 4G, 4x CPU) makes the synchronous unused
  JS/CSS dominate: top opportunities were `unused-javascript` (~310 KiB, ~1.5 s),
  `unused-css-rules` (~74 KiB), `unminified-css`, `unminified-javascript`.
- **Field metrics stay green** (CrUX): mobile LCP 1.5 s, CLS 0, CWV Passed — real
  users on fast connections get good LCP; the lab-vs-field gap is the synthetic
  throttle, not a real-world regression.
- Cache headers verified live: `/assets/css/quick-website.css` →
  `public, max-age=31536000, immutable`; `/assets/img/mm.jpg` → 30 days; versioned
  `?v=2026-08-17` URLs; sitemap `lastmod` = release date (B14).
- **Decision**: Tier 2 items below (maps lazy-load, JS minify/bundle, CSS purge)
  are the path to a >70 lab score. Not started this release — deferred.

## Deferred — Tier 2 (improvement / feature level)

- ~~Subset Font Awesome to the ~9 used icons~~ ✅ done in `perf/fa-subset`:
  `all.min.css` (59 KB) removed from the 4 bases; a hand-built `fa-subset.css`
  (~1.4 KB) + `fa-solid-subset.woff2` (2.7 KB vs 78 KB) load only on the ~13
  templates that use `fas` icons. Guardrail tests in
  `tests/test_fontawesome_subset.py` fail on any new icon until the subset is
  regenerated. Note: `quick-website.min.css` (59 KB) is a **stale build** (701
  rules vs 6,427 in the full file; swiper/tagsinput rules missing) — do NOT
  switch the templates to it; purge/rebase the theme instead.
- Minify + bundle JS into 2–3 files; unify `quick-website.js` vs `-min.js`
  variants (base_light and base_dark differ).
- Purge unused CSS from `quick-website.css` (573 KB theme, most unused on most
  pages) or inline critical CSS.
- Per-page asset loading via `{% block page_css %}` / `{% block page_scripts %}`:
  flatpickr, bootstrap-notify, maps, simplemde only where used.
- Google Maps lazy-load (IntersectionObserver) + defer — requires guarding the
  three `initMap` IIFEs in `quick-website.js` (currently they run eagerly at
  parse time; plain `defer` of the API breaks the homepage map).
- `srcset`/`sizes` + AVIF/WebP for images; `width`/`height` attributes.

## Deferred — Tier 3 (smart / architecture level)

- Asset build pipeline (esbuild/webpack/Flask-Assets): minify + content-hash
  filenames + purgecss, wired into the release process → safe immutable cache
  without manual `?v=` bumps.
- CI performance budget (Lighthouse CI or transfer-size check in pre-push) so
  regressions fail the gate.
- CDN (e.g., Cloudflare): brotli, HTTP/3, edge caching, on-the-fly image
  resizing, remove `Vary: Cookie` on static.
- Service worker (stale-while-revalidate) for the static shell.
- Replace the date-based `?v=` convention (`asset()` macro, `ASSET_VERSION` =
  deploy date) with content-hash fingerprinting; date-based versioning cannot
  bust assets for same-day hotfixes and couples caching to the release date.
