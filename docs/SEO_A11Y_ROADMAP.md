# SEO, Crawler/Agent & Accessibility Roadmap

<!-- encoding: utf-8 -->

Tracks agreed decisions, audit findings, and deferred ideas for making the site friendly to search engines, scanners/crawlers, and AI agents. Serves as the return point for deferred work.

Covers: metadata/OG decisions, robots/sitemap policy, JSON-LD/llms.txt, server-rendered lists, and deferred accessibility/perf work. Does not cover: the accessibility implementation itself (deferred), architecture — see `docs/ARCHITECTURE.md`, route registry — see `docs/API_REFERENCE.md`.

## 1. Decisions (agreed 2026-08-13)

| # | Decision | Where |
|---|----------|-------|
| D1 | Scope this round: SEO + crawler/agent friendliness. WCAG deferred to a manual one-off audit (separate PR). | — |
| D2 | Server-render JS-only lists (theses, diplomas themes, thesis-review) with progressive enhancement. | `flask_se_theses.py` `theses_search`, `se_scripts.js` |
| D3 | Add `/llms.txt` alongside `robots.txt`. | `src/static/llms.txt` |
| D4 | No new test deps for a11y; use manual axe/lighthouse later. | — |
| D5 | `og:url` → canonical URL (was `request.url`). | `base_dark.html`, `base_light.html` |
| D6 | Sitemap index: static `sitemap.xml` + per-year `sitemap-theses-<year>.xml` from FTS index; `lastmod` = per-thesis dates. | `src/sitemap.py` |
| D7 | Pre-rendered og-images in `src/static/assets/img/og/` (1200x630, one per section) + `apple-touch-icon`. **GUARDRAIL: re-generate images before push when design changes significantly.** | bases, `DESIGN_DECISIONS.md` |
| D8 | Sitemap `lastmod` = per-page real dates (deploy constant for static, DB timestamps for dynamic). | `src/sitemap.py` |
| D9 | `/.well-known/llms.txt` → 301 to root `/llms.txt` (single source for tooling that only probes `.well-known`). | `flask_se_static.py` |
| D10 | `/index.html` → real **301** to `/` (was default 302). | `flask_se_static.py` |
| D11 | Sitemap keeps exactly one canonical URL per resource: `/news/` only; `/news/index.html` dropped. | `src/sitemap.py` |
| D12 | RFC 9116 `security.txt` at `/.well-known/security.txt` (contact `dluciv@spbu.ru`) + `/security.txt` → 301 alias. | `src/static/.well-known/security.txt` |
| D13 | OpenSearch `/opensearch.xml` → `theses.html?search={searchTerms}` + `<link rel="search">` autodiscovery in the 4 bases. | `src/static/opensearch.xml`, bases |
| D14 | Section directory indexes `/bachelor/`, `/master/`, `/department/`, `/students/` → 301 to the section's representative page (directory-traversing agents no longer get 404). | `flask_se_static.py` `LEGACY_REDIRECTS` |
| D15 | robots.txt keeps `*` allow-all; explicit AI-crawler groups **not** added — a specific `User-agent:` group would override `*` for that bot, so each would need to repeat the sensitive disallow list; `*` already covers AI crawlers. | `src/static/robots.txt` |

## 2. Findings (audit 2026-08-13)

- `/theses.html` ships an empty `#ThesisList`; all content via `fetch('fetch_theses?...')` (`se_scripts.js:59,134,182`); same for diplomas themes + thesis-review list.
- **Verified NON-issue (audit false-positive, corrected 2026-08-13)**: initial audit flagged 4 "empty `<title>`" templates (`nooffer.html`, `scholarships/9.html`, `scholarships/10.html`, `theses_tmp.html`) — all actually render proper titles (multiline blocks). Only `theses_tmp.html` (admin temp-archive page) warrants `noindex` since it is internal-only and already sitemap-excluded.
- OG block missing in both `*_footer_white.html` bases.
- `og:url` = `request.url` (not canonical); no `apple-touch-icon`; default og-image `main-back.jpg`.
- Canonical missing on many public pages (contacts, research_directions, most scholarships, bachelor/master).
- `sitemap.py`: lastmod always today; arg-bearing rules excluded → `thesis_card` never indexed.
- `robots.txt` disallows only `/login.html`. No `humans.txt`, no `llms.txt`, no JSON-LD (partial microdata only).
- TODO.md:13-17: 3 OG defects (diploma theme textile leak, thesis_card whitespace, `/news/` empty description).
- GTM asymmetry: active in `base_light`, commented in `base_dark` (both have noscript iframe).
- SSR makes pagination query URLs crawlable — robots disallows `fetch_*`; sitemap stays parameterless.

## 3. Deferred ideas (return later — high value)

- WCAG 2.1 AA pass + optional `pytest-axe`/manual gate + `.skills/a11y-audit`.
- CSP + security headers (Flask `after_request` + `nginx/default.conf.template`).
- Asset hygiene: minified CSS default, `?v=`/fingerprint cache-busting, prune ~2,400 unused `assets/libs/` files.
- ~~Google Maps key hardcoded in HTML → config/server~~ ✅ done in `perf/maps-lazy`:
  key read from `configs/flask_se_maps.conf`/`SE_GOOGLE_MAPS_KEY` (gitignored),
  injected via `{% block se_maps_key %}` only on the 3 map pages; the maps API is
  now lazy-loaded (IntersectionObserver) instead of a sync script on every base.
- ~~Move from Google Maps to Yandex Maps~~ ✅ done in `feat/yandex-maps` (2026-08-19): the 3 map
  elements (index, contacts, bachelor_admission) now support **both providers** — Yandex Maps v3
  preferred, Google Maps fallback, and an inline **"Источник карты не задан"** placeholder when no key
  is configured. `flask_se_config.maps_config()` picks the active provider by priority
  (`YANDEX_MAPS_KEY` → `GOOGLE_MAPS_KEY`, env `SE_YANDEX_MAPS_KEY`/`SE_GOOGLE_MAPS_KEY` or
  `configs/flask_se_maps.conf` with `YANDEX_MAPS_KEY=`/`GOOGLE_MAPS_KEY=` lines; a legacy single-value
  file still counts as the Google key). `js/se_maps.js` lazily injects the active API
  (`ymaps3.ready` for Yandex, JSONP callback for Google); `quick-website.js` keeps the
  `window.__seMaps` registration contract and dispatches to `renderGoogle` (existing gray styles +
  InfoWindow) or `renderYandex` (`ymaps3.YMap` + `YMapDefaultSchemeLayer` + `YMapDefaultMarker`
  balloons). Deviations: the Yandex path uses the default scheme + pin markers — the Google grayscale
  `styles` and `DROP` animation have no ymaps3 equivalent. Guardrails: `tests/test_maps_lazy.py`
  (no sync API script, no key/provider leak, per-provider render + placeholder, initializer
  dispatch) and re-run `.tmp/predeploy_snapshot.py` + `.tmp/compare_snapshot.py` for the 3 map
  routes post-change.
- `WebSite` + `SearchAction` JSON-LD; convert remaining microdata to JSON-LD.
- Fix GTM asymmetry.
- Investigate legacy top-level `static/` dir (615 PDFs, not wired to Flask).
- **News section** (audit 2026-08-16): `/news/item.html?post=N` URLs are 302 chains to an
  external Tilda site (DDoS-Guard challenged), zero local content. Deferred content
  decision: host summaries locally + 301/canonical to external detail, or keep a local
  index. Add `/news/rss.xml` + pagination `canonical`/`rel=next|prev` + sitemap
  inclusion when re-architecting.
- **JSON-LD depth**: `Person` per staff member (with `sameAs`, email), `ScholarlyArticle`
  on thesis detail pages, `BreadcrumbList` site-wide, `ItemList` for archive listings.
- **`llms-full.txt`**: deep markdown dump of key program/staff content, cross-linked
  from `llms.txt` (llms.txt proposal's "links to markdown files" pattern).
- **EN variant + `hreflang`**: `html lang="ru"` is fixed today; a second language is a
  separate content project.

## 4. Declined

- None outright; everything above is deferred with a return path.

## 5. Execution (each PR carries a mandatory RETROSPECTIVES entry)

1. `feat/meta-audit` — titles, canonical sweep, OG fixes + parity + pre-rendered images, robots.txt, sitemap index, humans.txt. ✅ PR #208
1. `feat/ssr-lists` — SSR theses/diplomas/thesis-review, JS double-fetch guard, `aria-live`. ✅ PR #209
1. `feat/jsonld-llms` — JSON-LD blocks + `/llms.txt` + tests. ✅ PR #210
1. `feat/seo-agentic-hygiene` — `.well-known/llms.txt` alias, `/index.html`→301, section-index 301s, `security.txt`, OpenSearch, sitemap dedup. ✅ PR #223

PRs are stacked: each new PR branches from the previous PR's branch; merged one-by-one in completion order.

## 6. FAQ structured data decision

The FAQ page (`frequently_asked_questions.html`) already carries complete, valid `FAQPage` microdata (19 Q&A pairs via `itemprop="mainEntity"`). It was **not** converted to JSON-LD: converting adds duplication risk with no SEO gain since the microdata already produces the rich result. JSON-LD was added only where no structured data existed (Organization, WebSite+SearchAction, Course, BreadcrumbList). Revisit if the FAQ markup is ever refactored.
