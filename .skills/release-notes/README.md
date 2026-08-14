# release-notes

<!-- encoding: utf-8 -->

Generate end-user-friendly release notes for a GitHub release. Use when creating
or tagging a release (`vYYYY.MM.DD`). Produces a plain-English user summary
(Part 1) plus a developer changelog (Part 2) with an updated dependencies
table, major changes, contributors, and a compare link.

## Scope guard (hard rule)

- Write ONLY to `.tmp/release-notes.md` (the gitignored scratch folder). The
  `.tmp/` directory is created on demand; never leave the draft at the repo root.
- Do NOT modify any code, CI workflow, config, or documentation file.
- Do NOT create, edit, or publish a GitHub release — the CI workflow creates a
  draft on tag push (when `OPENCODE_ZEN_API_KEY` is set); the maintainer reviews
  and publishes it. Publishing the draft is what triggers the production deploy.
- Do NOT run git commands that change state (no commits, tags, pushes).

## When to load

- Before tagging a release — see `docs/DEVELOPMENT_PROCESS.md` §Release.
- Release-time drift fixes (dates, counts) live in `docs/RELEASE_CHECKLIST.md`
  — run that guardrail first, then generate notes.

## Steps

1. Determine the tag being released and the previous release tag. Both are
   passed as arguments: the current tag and the previous release tag. If the
   previous tag is not given, find it:
   `gh release list --repo spbu-se/spbu_se_site --limit 10 --json tagName --jq '.[].tagName'`
   (or `git tag --list 'v*' --sort=-version:refname`), filtering out the
   current tag.
1. Collect merged pull requests since the previous release:
   `gh pr list --repo spbu-se/spbu_se_site --state merged --base current --limit 100 --json number,title,mergedAt,author`
   Filter to PRs merged after the previous release. Keep newest-first order.
1. Run the PROMPT below with that PR list, then write the result to
   `.tmp/release-notes.md` (create `.tmp/` if missing).

## PROMPT

You are writing the release notes for the website of the SPbU System Programming
Department (https://se.math.spbu.ru). The site publishes department news, thesis
topics, student practices, thesis reviews, and admission information for
bachelor's and master's applicants. The main audience is prospective students,
current students, and faculty — mostly not programmers.

Write release notes in SIMPLE ENGLISH. Use short sentences, common words, and no
jargon. Structure them in two clearly separated parts:

PART 1 — End-user summary (warm, simple, non-technical):

- A short 2-4 sentence paragraph titled "What's new" describing, in plain
  everyday language, what this release brings to a visitor of the site. Focus
  on real user value: updated information, new pages or sections, reliability,
  ease of use.
- Then a short bulleted list "Key improvements" (3-6 bullets) of the most
  user-visible improvements, each in one plain sentence. NO jargon like
  "backend", "refactor", "CI", "lint", "dependency", "lockfile", "deploy".

PART 2 — Developer reference, in this order:

1. Heading "For developers".
1. A heading "### Updated dependencies" with a markdown table of every
   dependency that changed since the previous release. Columns: `Dependency`
   and `Version`. Use the version reached in this release. One row per
   dependency. If nothing changed, omit this section. Do NOT list dependency
   bumps as bullets anywhere.
1. A heading "### Major changes" with a bullet list of only significant
   commits: features, fixes, large PRs, and major improvements. In Conventional
   Commits style: `- fix: short description (#123)`. Drop routine
   `chore(deps)`, `docs`, `ci`, and other internal bumps — they belong in the
   dependencies table or the compare link, not here.
1. A "Contributors" line listing the human authors of the merged PRs. Remove
   obvious bots (dependabot, github-actions, renovate, etc.). Format as
   `Contributors: [@username](https://github.com/username), ...`. Mark new
   contributors (first PR in this repository) in bold with `(new)`:
   `**@username (new)**`.
1. The last line, exactly:
   `Detailed comparison with previous release vYYYY.MM.DD: <https://github.com/spbu-se/spbu_se_site/compare/vPREV...vCURRENT>`
   using the actual previous tag and current tag.

RULES:

- Part 1 must be genuinely user-facing: talk about what a site visitor can now
  see or do, what information is new or fixed. Do NOT translate developer
  terms — rephrase them into plain words.
- Part 1 must NOT mention: PR numbers, CI, linters, dependency versions,
  lockfiles, Dependabot, or site internals.
- Keep Part 1 concise and friendly. Part 2 is the developer log.
- Separate the two parts with a `---` divider.

INPUT — merged changes for this release (Conventional-Commits-style titles,
newest first), with author login per PR:
<insert the PR list here>

Current tag: <current tag>
Previous release tag: <previous tag>
