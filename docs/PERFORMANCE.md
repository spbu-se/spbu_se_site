# PERFORMANCE.md

<!-- encoding: utf-8 -->

Scope: performance optimization roadmap for se.math.spbu.ru — baseline
measurements, shipped Tier 1 work, and the deferred ideas/goals backlog.

Covers: performance baseline/measurements, shipped optimizations (Tier 1, Font
Awesome subset, app-side cache headers, asset build pipeline), deferred Tier
2/3 ideas, post-deploy re-evaluation return-item. Does not cover: SEO/agentic
roadmap — see `docs/SEO_A11Y_ROADMAP.md`, general quality tiers — see
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

## Post-release measurement (2026-08-18, v2026.08.18 live)

Tier 2 campaign shipped (build pipeline, maps lazy-load, JS deferral). Live
content verified against the pre-deploy snapshot
(`.tmp/predeploy_snapshot/` → `.tmp/postdeploy_snapshot/` via
`.tmp/compare_snapshot.py`):

- **Expected changes present**: all 4 bases serve `quick-website.min.css`/`.min.js`
  (was the unminified 573 KB css); every script carries `defer`; `SE_ON_READY`
  helper in each base `<head>`; hero `preload` on `/`; zero sync
  `maps.googleapis.com/maps/api/js` script; `/news/` loads no maps code.
- **Maps key was unprovisioned at deploy**: `SE_GMAPS_KEY=""` → `se_maps.js`
  early-returns, so the 3 map pages (index, contacts, bachelor_admission) render
  an empty 500px map box. Fixed by admin setting a provider key on prod +
  restart — since `feat/yandex-maps` the site is **dual-provider** (Yandex
  preferred via `SE_YANDEX_MAPS_KEY`, Google fallback via `SE_GOOGLE_MAPS_KEY`),
  and with neither key set the box shows the "Источник карты не задан"
  placeholder instead of an empty box. Guardrail: checklist B16.
- **`?v=` / sitemap `lastmod` show today, not the release date**: `SE_SITE_LASTMOD`
  is unset on prod, so `site_deploy_date()` falls back to `date.today()`. Same-day
  it matches the previous release's `?v=`; it self-corrects next day. Not a cache
  or content issue (B14 deviation only).
- Re-measure lab mobile Lighthouse after the maps key is provisioned; record the
  result here and in `RETROSPECTIVES.md` (return-item).

## Deferred — Tier 2 (improvement / feature level)

- ~~Subset Font Awesome to the ~9 used icons~~ ✅ done in `perf/fa-subset`:
  `all.min.css` (59 KB) removed from the 4 bases; a hand-built `fa-subset.css`
  (~1.4 KB) + `fa-solid-subset.woff2` (2.7 KB vs 78 KB) load only on the ~13
  templates that use `fas` icons. Guardrail tests in
  `tests/test_fontawesome_subset.py` fail on any new icon until the subset is
  regenerated.
- ~~Minify + bundle JS into 2–3 files; unify `quick-website.js` vs `-min.js`
  variants~~ ✅ done in `perf/build-pipeline`: bases now serve the regenerated
  `quick-website.min.js` (terser, from the committed source).
- ~~Purge unused CSS from `quick-website.css`~~ ✅ done in `perf/build-pipeline`:
  6,427 → ~1,744 rules; 595 KB → ~140 KB min. All literal template classes kept
  (guardrail `tests/test_asset_pipeline.py` mirrors purgecss's all-classes rule).
- ~~Per-page asset loading via `{% block page_css %}` / `{% block page_scripts %}`:
  maps only where used~~ ✅ maps handled by `perf/maps-lazy` (key block + lazy
  loader only on base_dark). Remaining: flatpickr, bootstrap-notify, simplemde
  only where used.
- ~~Defer jquery/bootstrap + remaining sync libs; convert inline `$()` templates
  to an SE_ON_READY queue~~ ✅ done in `perf/js-defer`: all scripts deferred
  (document order preserved; `async` removed from jquery-dependent libs);
  `seReady(fn)` helper in every base; 4 templates converted to `seReady`/vanilla
  DOM; homepage hero preload. Guardrails in `tests/test_js_deferral.py`.
- ~~Google Maps lazy-load (IntersectionObserver) + defer~~ ✅ done in
  `perf/maps-lazy`: the three `initMap` IIFEs in `quick-website.js` now register
  into `window.__seMaps` (no `google.maps` at parse time); `js/se_maps.js`
  (defer) injects the API only when a map element scrolls into view. The sync
  maps `<script>` was removed from all 4 bases (only index/contacts/
  bachelor_admission have maps) and the API key moved to config
  (`flask_se_maps.conf` / `SE_GOOGLE_MAPS_KEY`, gitignored) — injected only on
  the 3 map pages via `{% block se_maps_key %}`. Superseded by the
  dual-provider renderer (`feat/yandex-maps`) — see §Shipped — Tier 2 maps.
- `srcset`/`sizes` + AVIF/WebP for images; `width`/`height` attributes.

## Shipped — Tier 2 build pipeline (PR: perf/build-pipeline)

- `package.json` + `scripts/build-assets.mjs` (`npm run build`): purgecss
  (content = all templates + all JS under assets, greedy safelist for dynamic
  JS class families) → esbuild minify → `quick-website.min.css`; terser →
  `quick-website.min.js`. Both outputs are committed (build-and-commit).
- The committed `quick-website.min.css` was a **stale build** (60 KB / 701 rules
  vs 6,427 in source) — regenerated now: ~140 KB / ~1,744 rules. The 4 bases +
  `admin/master.html` reference the min files; the 595 KB unminified source css
  stays committed as the build input.
- Deleted stale build remnants: `.css.map`/`.js.map` files, the `css/min/`
  directory, and the unused `quick-website-dark*` variant (not referenced by any
  template).
- CI `assets` job (ci.yml): `npm ci` → `npm run build` → `git diff --exit-code`
  on both min outputs, so committed artifacts can never drift from the sources.
  Local guardrail tests: `tests/test_asset_pipeline.py` (min files served, not
  stale, every template class survives the purge, every `asset()` reference
  resolves).
- Decisions: content-hash `?v=` replacement deferred (date-based `?v=` still
  busts correctly per release); Lighthouse CI budget deferred. See the PR-3
  retrospective.

## Shipped — Tier 2 maps (lazy-load, then dual-provider)

- The Google Maps JS API was a **synchronous ~350 KB script on all 4 bases** —
  removed. Only 3 pages have maps (index, contacts, bachelor_admission), all
  base_dark.
- `perf/maps-lazy` replaced the eager `google.maps.event.addDomListener(...)`
  triggers with registration into `window.__seMaps` (`{id, init}`);
  `feat/yandex-maps` then made the renderer **dual-provider**: the 3
  initializers feed a shared `SEInitMap(el, markers)` that dispatches on
  `window.SE_MAPS_PROVIDER` to `renderGoogle` (gray `styles`, `DROP`,
  InfoWindow) or `renderYandex` (`ymaps3.YMap` + `YMapDefaultSchemeLayer` +
  `YMapDefaultMarker` balloons). No `google.maps`/`ymaps3` is touched at parse
  time.
- `js/se_maps.js` (defer, base_dark only): IntersectionObserver on the map
  elements → injects the active provider's API (Yandex v3 via `ymaps3.ready`,
  Google via `?key=...&callback=__seGmapsLoaded`) → runs the registered
  initializers. No IO support → load immediately. No provider configured →
  early return, and the map box renders the inline "Источник карты не задан"
  placeholder instead of an empty box.
- API keys moved out of HTML into config: `configs/flask_se_maps.conf`
  (gitignored, `YANDEX_MAPS_KEY=`/`GOOGLE_MAPS_KEY=` lines) or env
  `SE_YANDEX_MAPS_KEY`/`SE_GOOGLE_MAPS_KEY`; `flask_se_config.maps_config()`
  picks the active provider by priority Yandex → Google → none. Template globals
  `se_maps_provider`/`se_maps_key` render only on the 3 map pages via
  `{% block se_maps_key %}`. Pages without maps never expose the key or request
  the API.
- Guardrail tests: `tests/test_maps_lazy.py` (no sync API script of either
  provider in bases, no key/provider leak, loader wiring, initializer dispatch,
  per-provider + placeholder rendered pages).
- Post-deploy verify: maps render on index/contacts/bachelor; zero maps requests
  on `/news/`.

## Shipped — Tier 2 JS deferral (PR: perf/js-defer)

- All scripts in the 4 bases now carry `defer` (was a mix of sync and
  `async defer`): jquery, bootstrap, the theme bundle, all libs, and the
  first-party scripts (`se_scripts.js`, `se_practice_script.js`,
  `se_maps.js`). Deferred scripts run in document order after parsing, before
  DOMContentLoaded — the parser is no longer blocked on ~200 KB of script.
- **`async` removed from the jquery-dependent libs** (sticky-kit, imagesloaded,
  bootstrap-notify, svg-injector, in-view, autosize): `async` would let them
  execute before deferred jquery and throw `jQuery is not defined`. Plain
  `defer` preserves the jquery-first order.
- **SE_ON_READY helper** (`seReady(fn)`) defined in every base `<head>`: inline
  content-block scripts can no longer rely on `$` at parse time (deferred
  jquery is not loaded yet), so templates queue callbacks flushed on
  DOMContentLoaded (jquery already loaded by then). Converts the old
  `$(document).ready(...)` pattern.
- Inline jquery converted in the 4 templates that used it:
  `practice/{staff/reports_staff,thesis_staff,admin/thesis_admin}` now use
  `seReady(...)` for `document.title`; `practice/student/goals_tasks.html` uses
  vanilla `querySelectorAll` for its task-list reset (no jquery dependency).
  No template calls `$()`/`$(document).ready` inline at parse time anymore.
- LCP: the homepage hero (`main-back.jpg`, a CSS background) is `<link rel="preload" as="image">`-ed in index's headers block so the LCP image
  starts fetching immediately.
- Guardrail tests: `tests/test_js_deferral.py` (core scripts deferred + ordered
  in all 4 bases, light-base libs deferred, SE_ON_READY defined before content,
  no inline `$(document).ready`/`$()` in templates, se_maps.js still deferred).
- Pre-deploy snapshot of main pages + assets in `.tmp/predeploy_snapshot/`
  (capture via `.tmp/predeploy_snapshot.py`, compare post-deploy via
  `.tmp/compare_snapshot.py`).

## Deferred — Tier 3 (smart / architecture level)

- Asset build pipeline content-hash fingerprinting: minify + purgecss now ship
  (`perf/build-pipeline`); the remaining Tier 3 piece is **content-hash
  filenames** replacing the date-based `?v=` (manifest read by Flask) so
  same-day hotfixes bust assets without a date change.
- CI performance budget (Lighthouse CI or transfer-size check in pre-push) so
  regressions fail the gate.
- CDN (e.g., Cloudflare): brotli, HTTP/3, edge caching, on-the-fly image
  resizing, remove `Vary: Cookie` on static.
- Service worker (stale-while-revalidate) for the static shell.
- Replace the date-based `?v=` convention (`asset()` macro, `ASSET_VERSION` =
  deploy date) with content-hash fingerprinting; date-based versioning cannot
  bust assets for same-day hotfixes and couples caching to the release date.
