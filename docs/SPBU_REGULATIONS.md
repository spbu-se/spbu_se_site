# SPbU Website Regulations

<!-- encoding: utf-8 -->

Mapping of the СПбГУ «Регламент создания, функционирования и закрытия сайтов СПбГУ» (Приказ № 11763/1 от 16.09.2025, replaces № 8254/1 от 2018) to this site's implementation, with the compliance decisions made per clause.

Covers: the assessed clauses and their status, the decisions behind each status. Does not cover: GDPR/152-ФЗ privacy compliance — see `docs/PRIVACY_COMPLIANCE.md`, the SEO/accessibility roadmap — see `docs/SEO_A11Y_ROADMAP.md`.

## Source

- «Регламент создания, функционирования и закрытия сайтов СПбГУ», утверждён Приказом № 11763/1 от 16.09.2025 (replaces Приказ № 8254/1 от 2018).
- Local copies of the приказ + appendices: `.tmp/spbu-regulation/` (gitignored scratch — archive them on the shared drive when this batch ships).

## Compliance status

| Clause | Requirement (gist) | Status | Decision / note |
|--------|--------------------|--------|-----------------|
| 3.1.2 | Site must be published under a domain coordinated with СПбГУ | ✅ compliant | `se.math.spbu.ru` is a university subdomain |
| 3.1.3 | Contact/operator info present | ✅ compliant | Footer + `/contacts.html` |
| 3.1.5 | Data must be stored on the operator's territory | ✅ compliant | Self-hosted on university infrastructure |
| 3.1.6 | «Версия для слабовидящих» **or** font size ≥ 14 pt | ✅ implemented | Accessibility-mode toggle shipped v2026.08.31 (`css/a11y.css`, footer link «Версия для слабовидящих», 18 px root font, high-contrast palette) |
| 3.1.9 | Page header must contain a link to `https://spbu.ru` | ✅ satisfied | Navbar SPbU logo links to `https://spbu.ru/`; the SPbU topbar is **removed** (service dead — `topbar.spbu.ru/loader.js` returns HTTP 410 Gone) |
| 3.1.12 | Tag-manager container required | ⏸️ **deferred** | Site has none (GTM removed v2026.08.20). User decision 2026-08-31: postpone — revisit with the consent plan in `docs/PRIVACY_COMPLIANCE.md` §4 before re-enabling; tracked in `TODO.md` |
| 3.1.14 | Consent notice must name the service and operator | ✅ mostly compliant | Consent banner names Yandex Metrica + operator СПбГУ / ООО «Яндекс» |
| 3.1.15 | Copyright format «© Санкт-Петербургский государственный университет, \<текущий год>» | ✅ implemented | Plan B shipped v2026.08.31: required СПбГУ line added **and** the department line kept (4 base templates) |
| 3.1.16 | Site must not violate third-party rights / licensing | ✅ compliant | Self-hosted assets; no unlicensed third-party content |

## Decisions

1. **Topbar removed (v2026.08.31)** — the topbar service is retired by СПбГУ (`loader.js` → 410 Gone). §3.1.9 only mandates a header link to spbu.ru, which the navbar logo already provides, so removal is compliant. CSP entries dropped from `script-src`/`connect-src`; preconnect/dns-prefetch + injector removed from all 4 bases.
1. **Accessibility mode implemented (v2026.08.31)** — chosen over a global font bump so normal visitors keep the current design. Toggle link in the footer (next to cookie settings), state persisted in `localStorage` (`se-a11y-mode`), applied pre-paint by a nonce head script to avoid a flash. See `src/static/assets/css/a11y.css`.
1. **Copyright plan B (v2026.08.31)** — the required «© Санкт-Петербургский государственный университет, {{ current_year }}» line is added above the existing department line; both use the `{{ current_year }}` template global, so `docs/RELEASE_CHECKLIST.md` A1 note stays accurate.
1. **Tag manager deferred** — §3.1.12 is the only open gap. It conflicts with the privacy posture (consent-gating analytics is hard to reconcile with a mandated tag-manager container); postponed until the §4 full-compliance plan is designed. See `TODO.md`.

## Related docs

- `docs/PRIVACY_COMPLIANCE.md` — cookie/consent inventory, Metrica gating, GTM removal record.
- `docs/SEO_A11Y_ROADMAP.md` — CSP + accessibility backlog.
- `docs/RELEASE_CHECKLIST.md` — release-time copyright drift check.
