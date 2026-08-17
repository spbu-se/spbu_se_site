# PERFORMANCE.md

<!-- encoding: utf-8 -->

Scope: performance optimization roadmap for se.math.spbu.ru — baseline
measurements, shipped Tier 1 work, and the deferred ideas/goals backlog.

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
- Host nginx ticket (`.tmp/nginx_tuning.md`): gzip + immutable cache for
  `/assets/css|js|libs/`, 30-day cache for `/assets/img/`. **gzip live** (verified
  2026-08-17); the cache half is re-issued as a follow-up ticket (all `/assets/*`
  still `Cache-Control: no-cache`).
- Baseline Lighthouse JSON: `.tmp/baseline_lighthouse.json`.

## Return-item (mandatory re-evaluation)

Once the Tier 1 PR is merged **and** the nginx changes are live:

1. Re-run `npx lighthouse https://se.math.spbu.ru/ --only-categories=performance --form-factor=mobile` and record the score here.
1. Record `curl -sI` headers for `/assets/css/quick-website.css` (expect
   `Content-Encoding: gzip`, `Cache-Control: ... immutable`).
1. Decide whether to start Tier 2 items below; update this file with measured
   before/after numbers and the retrospective.

## Deferred — Tier 2 (improvement / feature level)

- Subset Font Awesome to the ~9 used icons (or FA SVG/JS subset) — full
  `all.min.css` (59 KB) for a handful of `fas` icons.
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
