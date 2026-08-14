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
- Google Maps key hardcoded in HTML (`base_dark.html:346`) → config/server.
- `WebSite` + `SearchAction` JSON-LD; convert remaining microdata to JSON-LD.
- Fix GTM asymmetry.
- Investigate legacy top-level `static/` dir (615 PDFs, not wired to Flask).

## 4. Declined

- None outright; everything above is deferred with a return path.

## 5. Execution (each PR carries a mandatory RETROSPECTIVES entry)

1. `feat/meta-audit` — titles, canonical sweep, OG fixes + parity + pre-rendered images, robots.txt, sitemap index, humans.txt.
1. `feat/ssr-lists` — SSR theses/diplomas/thesis-review, JS double-fetch guard, `aria-live`.
1. `feat/jsonld-llms` — JSON-LD blocks + `/llms.txt` + tests.

PRs are stacked: each new PR branches from the previous PR's branch; merged one-by-one in completion order.
