# Privacy & Personal Data Compliance

<!-- encoding: utf-8 -->

Audit of how `se.math.spbu.ru` handles cookies, analytics, and personal data under the EU GDPR and Russian federal law 152-ФЗ «О персональных данных»; the mitigation shipped in v2026.08.20 (Google Tag Manager removed, Yandex Metrica dormant); and the **full-compliance implementation plan (next HIGH PRIORITY task)** that enables Yandex Metrica (and GTM, if ever re-introduced) safely and compliantly.

Covers: applicable law, cookie/third-party/personal-data inventory, legal-basis analysis, the disablement shipped in this release, and the ranked improvement plan with acceptance criteria. Does not cover: security headers (see `docs/SEO_A11Y_ROADMAP.md`), legal advice (this document is not counsel), or the accessibility/SEO backlog.

## 1. Applicable law and jurisdiction

| Regime | Applies to | Relevance |
|--------|-----------|-----------|
| **152-ФЗ** «О персональных данных» | Data subjects in Russia | Primary regime: operator duties (Roskomnadzor notification, consent, rights under ст. 14), cross-border transfers |
| **GDPR** (EU 2016/679) | Data subjects in the EU/EEA (site is globally reachable) | Art. 6 legal basis, Art. 7 consent, transparency (Art. 13), rights, processor agreements |
| **ePrivacy Directive** (EU 2002/58/EC as amended) | EU visitors | Cookie/analytics consent separate from GDPR — applies to any non-strictly-necessary cookie (Yandex Metrica sets cookies) |

The operator is the Saint Petersburg State University (СПбГУ); the department (кафедра системного программирования, Математико-механический факультет) runs the site on SPbU infrastructure. Whether a specific process falls under the university charter (152-ФЗ ч. 1 ст. 6 п. 5) vs. requires consent must be confirmed by SPbU's legal office — flagged as a decision in §5.

## 2. Current-state audit (baseline: v2026.08.18, before the mitigation)

### 2.1 Cookies and local storage

| Storage | Type | Purpose | Status | Consent needed? |
|---------|------|---------|--------|-----------------|
| `se_session` | first-party cookie (HttpOnly, SameSite=Lax, `Secure` gated on `SE_COOKIE_SECURE`) | Flask session: auth, CSRF, flash messages | Always set | No — strictly necessary (ePrivacy exemption; GDPR Art. 6(1)(b)/(f)) |
| `se_consent` | first-party cookie (SameSite=Lax) + `se_consent_choice` localStorage | Stores the granular consent decision (`essential[,statistics][,marketing]`); written by `js/se_consent.js`, read by Flask to gate analytics | Set after the banner decision; the server renders no optional tracker before it | No — it *is* the consent record (ePrivacy Art. 7/GDPR requires consent to be provable) |
| `modal_cookies` | localStorage | Remembers the legacy cookie-banner choice | **Removed in the consent-gate PR** (replaced by `se_consent`) | N/A |
| `_ym_*` cookies (`_ym_uid`, `_ym_d`, `_ym_isad`, …) | third-party (Yandex Metrica) | Visit statistics | **Dormant** — no counter id configured; when provisioned, the snippet renders only for visitors who accepted the `statistics` category | **Yes** (ePrivacy/GDPR) once enabled |
| `_ga*` / GTM cookies | third-party (Google) | Analytics/marketing via GTM | **Removed in v2026.08.20** | Was required — GTM ran without consent (see §2.5) |

### 2.2 Third-party services

| Service | Domain | State | What it receives | Role |
|---------|--------|-------|------------------|------|
| Google Tag Manager (`GTM-NGT2J3Z`) | `googletagmanager.com` | **REMOVED v2026.08.20** | page URL, referrer, User-Agent, IP, client identifiers | processor/controller — ran without consent |
| Yandex Metrica | `mc.yandex.ru` | **Consent-gated** (snippet renders only when a counter id is configured AND the visitor accepted the `statistics` category) | page URL, referrer, UA, IP, optional clickmap | processor — Yandex LLC processes on behalf of the operator |
| SPbU topbar | `topbar.spbu.ru` | Active on all 4 bases | loads the SPbU header bar; may set SPbU-first-party cookies | first-party component of SPbU |
| Yandex Maps v3 / Google Maps | `api-maps.yandex.ru`, `maps.googleapis.com` | **Dormant** (no key — «Источник карты не задан» placeholder) | IP, geolocation context when a map is active | processor |
| Google / VK OAuth login | `accounts.google.com`, `oauth.vk.com`, `oauth.yandex.ru` | Active | email + identity claims to create/link the account | identity provider |

### 2.3 Personal-data inventory (what the site itself stores)

| Data | Storage | Purpose | Retention today |
|------|---------|---------|-----------------|
| Account: name, email, password hash | `users` table (sqlite) | authentication, personal pages | while the account is active; **purged (login data) on account deletion** — see §4.7 deletion criterion |
| Avatar upload | static upload dir | profile display | until account deletion |
| Practice/VKR submissions: student full name, group, supervisor, work text, reviewer notes | `practice` / `theses` tables | educational process (department duty) | per university archival requirements |
| Diplomas themes | `diploma_themes` table | educational process | per university archival requirements |
| News posts, votes | `news` table | content publishing | for the lifetime of the publication |
| OAuth identifiers (Google/VK) | users table | account linking | until account deletion |

### 2.4 Legal-basis analysis

- **Educational-process data** (practice/VKR, diplomas, theses): 152-ФЗ ч. 1 ст. 6 п. 5 (processing necessary for functions assigned to the operator by law — university charter) / GDPR Art. 6(1)(b) contract (and (e) public interest for a public university). This is the strongest basis and needs only a privacy notice, not separate consent.
- **Account/registration**: 152-ФЗ ст. 6 п. 5 (or consent п. 1); GDPR Art. 6(1)(b) — contract for the service. Notice required.
- **Analytics (Metrica; previously GTM)**: 152-ФЗ — legitimate-interest (п. 5) or consent (п. 1) — department must pick; GDPR/ePrivacy — **consent required for the cookies**, independent of Art. 6 basis.

### 2.5 Gaps found before the mitigation

1. **GTM ran analytics/marketing tags without any consent gate** — non-compliant for EU visitors (ePrivacy cookie consent, GDPR Art. 7) and undocumented under 152-ФЗ.
1. **No privacy policy page** — no operator info, data categories, purposes, retention, or rights under 152-ФЗ ст. 14 / GDPR Art. 13.
1. **Cookie banner was partial** — present only in `base_dark.html`/`base_dark_footer_white.html`, absent from the light templates; and it never actually gated analytics (GTM loaded regardless).
1. **No retention policy** — user/practice data stored indefinitely.
1. **No granular consent** — all-or-nothing, non-retractable, not linked to a policy document.
1. **Cross-border/open questions** — Google services imply data flows to the EU/US (SCCs / Roskomnadzor cross-border analysis); Yandex Metrica keeps data in RU.

## 3. Mitigation shipped in v2026.08.20 — disable first, implement fully later

Strategy for this release: achieve a defensible baseline by **removing the unsafe features entirely**, then implement full support as the next task.

1. **GTM removed from all 4 base templates** — head snippet, noscript iframe, and the `googletagmanager.com` preconnect/dns-prefetch are gone. The site makes **zero** requests to `googletagmanager.com` (verified live post-deploy: `curl -s <page> | rg googletagmanager` → no match).
1. **Yandex Metrica wired config-driven and dormant** — counter id from the gitignored `configs/flask_se_metrica.conf` or env `SE_YANDEX_METRICA_ID`, validated as digits-only (`flask_se_config.metrica_id()`). The snippet (`mc.yandex.ru/metrika/tag.js`) renders **only** when an id is provisioned; until the admin adds one the site makes no analytics requests. Even when provisioned, the shipped snippet does **not** enable Webvisor (no session recording).
1. **CSP plan updated** — `googletagmanager.com` dropped from the `docs/SEO_A11Y_ROADMAP.md` allowlist, `mc.yandex.ru` added.
1. **Guardrail tests** — `tests/test_analytics.py`: no `googletagmanager`/`GTM-`/`dataLayer` anywhere in `src/templates`, metrica rendered only with an id.

**Compliance posture after this release**: first-party `se_session` (strictly necessary) + SPbU topbar + dormant maps; no third-party analytics cookies set → defensible under ePrivacy/GDPR for EU visitors and low-risk under 152-ФЗ.

## 4. FULL COMPLIANCE IMPLEMENTATION

Goal: enable Yandex Metrica (and GTM, if the department wants it back) with proper consent, transparency, and 152-ФЗ/GDPR safeguards. Each item has an owner column — repo work (done/here) vs. department/legal action (must be confirmed outside the repo). **Repo-side items shipped in the `feat/privacy-compliance` PR (2026-08-20); dept/legal items remain tracked below.**

### 4.1 Consent management (repo — shipped)

- Replace the dark-only `cookiealert` with a **consent banner on all 4 bases** offering granular choices: *essential* (always on), *statistics* (Yandex Metrica), *marketing* (GTM/Google, if re-enabled). Default-off.
- Store the choice (localStorage + a marker cookie), allow re-decision from the footer, and **gate snippet loading on consent** — do not even load `mc.yandex.ru/metrika/tag.js` until accepted.
- Banner text links to the privacy policy (§4.4).

### 4.2 GTM consent-mode wiring (repo, only if re-introduced)

- Load the GTM container with consent defaults; each tag is bound to a consent category so **no tag fires before acceptance** (GTM built-in consent mode / `gtag('consent', …)`).
- Ensure no PII is sent to Google (no email/name in dataLayer beyond what a tag explicitly needs).

### 4.3 Yandex Metrica privacy settings (dashboard, dept action + snippet defaults — defaults shipped)

- Keep `webvisor:false` (no session recording), `clickmap` off or lean, IP truncated; set data-retention limits in the Metrica dashboard.
- Confirm the department holds a Metrica **operator agreement** (Yandex acts as processor under 152-ФЗ) and enable Metrica's consent-integration features so the counter stops for users who decline.

> Shipped snippet defaults: `webvisor` is not enabled and `clickmap: false` (the old snippet's `clickmap: true` was dropped) — matching decision §5 #2 (no Webvisor; clickmap only if explicitly wanted). Retention limits and the Yandex operator agreement remain dashboard/dept actions.

### 4.4 Privacy policy page (repo — shipped draft + legal copy by dept)

- New `/privacy.html` (clone the `/n` static-page pattern), footer link on all 4 bases, entry in the sitemap.
- Content (to be drafted/approved by SPbU legal): operator identity + registered details; categories of data (§2.3); purposes and legal basis (§2.4); cookies list (§2.1); analytics providers and their role (§2.2); retention periods (§2.3 → define); user rights under 152-ФЗ ст. 14 (access, rectification, deletion) and GDPR Art. 15-22; contact for requests; date of last update.

> Shipped draft (`src/templates/privacy.html`, route `/privacy.html`, auto-sitemapped) links the official SPbU personal-data policy and the 05.06.2026 Metrica consent doc, names СПбГУ as operator (199034, СПб, Университетская набережная, 7–9), lists data categories/legal basis/cookies, and the rights under 152-ФЗ ст. 14 / GDPR. Final legal copy approval is SPbU legal's (acceptance criterion §4.7).

### 4.5 152-ФЗ operator obligations (dept/legal action, tracked here)

- Confirm the Roskomnadzor notification (уведомление) covers these processing operations (SPbU is likely already a registered operator — extend the scope). **Working assumption recorded 2026-08-21 (decision §5): SPbU is already a registered operator; the scope extension is tracked, not blocking repo work.**
- Execute/confirm a processing instruction (поручение на обработку) with Yandex for Metrica.
- Cross-border: Metrica = RU storage (OK); Google services = EU/US flows → GDPR SCCs and Roskomnadzor cross-border analysis before re-enabling GTM/Maps.
- Add a consent statement to forms that collect personal data where no charter basis applies (legal review needed). **Repo-side: notice text shipped** — `src/templates/consent_notice.html` («Отправляя форму, вы соглашаетесь…» + policy link) included on registration, practice, thesis-review, and internship forms; legal review of the wording remains dept/legal action.

### 4.6 Supporting hardening (repo)

- Ship the security-headers/CSP plan (`docs/SEO_A11Y_ROADMAP.md` §CSP) — limits tracking-injection surface and reduces data exposure.
- `Referrer-Policy: strict-origin-when-cross-origin` (already planned) trims referrer leakage to analytics providers.
- Define a session/remember-me lifetime policy in the privacy policy.

### 4.7 Acceptance criteria (definition of done)

- [x] Consent banner on all bases; analytics snippet loads only after acceptance (asserted by `tests/test_analytics.py` + `tests/test_consent.py`: no `mc.yandex.ru` in DOM before consent).
- [x] User data export (right of access / portability under 152-ФЗ ст. 14 / GDPR Art. 15, 20) — `/profile/export.zip` streams a ZIP with `account.json` (account data minus `password_hash`) + `content.json` (owned records); asserted by `tests/test_auth_views.py::TestUserExport`.
- [x] Account deletion (right to be forgotten / GDPR Art. 17) — `/profile/delete` soft-deletes the account (clears email, password hash, OAuth ids, avatar, contact; keeps names for published-content attribution); login blocked on all fronts; published content retained intact. Decision §5 #6 applied; asserted by `tests/test_auth_views.py::TestUserDelete`.
- [ ] Metrica provisioned on prod → counter fires only for consenting visitors; Webvisor off; retention configured (**repo done**; admin must provision `configs/flask_se_metrica.conf` and set Metrica retention in the dashboard). **Gated on: merge to `current` AND legal sign-off** (RKN scope + Yandex processing instruction + copy approval).
- [x] `/privacy.html` live, linked from all bases, sitemap'd (draft shipped; copy approval pending — tracked at §4.4). Retention terms shipped (§5 #5 tiered decision).
- [ ] Roskomnadzor scope + Yandex processing instruction confirmed (out-of-repo sign-off recorded). **Working assumption: SPbU is already a registered operator — scope extension tracked, not blocking.**
- [ ] If GTM re-enabled: consent-mode verified (no tag before consent) + cross-border analysis documented (GTM stays removed per §5 #1).
- [ ] Legal review sign-off (human) recorded in this doc.

## 5. Decisions needed from the department

| # | Question | Default stance | Owner |
|---|----------|----------------|-------|
| 1 | Should GTM ever return? User directive for v2026.08.20: *"site can use only Yandex Metrica"*. | Keep GTM removed; treat re-enable as an explicit decision | Department |
| 2 | Webvisor/clickmap for Metrica at all? | No Webvisor; clickmap only if explicitly wanted (**repo shipped `clickmap: false`**) | Department |
| 3 | Which legal basis for analytics under 152-ФЗ (consent vs. legitimate interest)? | Consent (cleanest; also satisfies ePrivacy) | SPbU legal |
| 4 | Privacy-policy copy owner | SPbU legal drafts; department reviews (**draft shipped in-repo**) | SPbU legal |
| 5 | Data retention periods for user/practice data | **DECIDED 2026-08-21 — tiered + fixed terms**: `se_session` 24h, `se_consent` 1y, account until deletion, educational records per university archival rules, publications for their lifetime. Shipped in `privacy.html` §Сроки хранения данных. | Department + legal |
| 6 | Account deletion: policy for removing a user account and its content (right to be forgotten) | **DECIDED 2026-08-21 — fired-employee model**: all published materials (practices, votes, posts, etc.) stay; the account (login, email, password, OAuth links, avatar) is removed. Implemented as soft-delete `/profile/delete` (shipped) — names kept for attribution. | Department + legal |

## 6. Cross-references

- CSP/security-headers plan: `docs/SEO_A11Y_ROADMAP.md` (allowlist updated for GTM removal + Metrica).
- Config pattern (gitignored `configs/flask_se_*.conf` + env override): `src/flask_se_config.py`.
- Metrics guardrails: `tests/test_analytics.py`; maps guardrails: `tests/test_maps_lazy.py`.
- Release guardrail: `docs/RELEASE_CHECKLIST.md` (B16 verify).
