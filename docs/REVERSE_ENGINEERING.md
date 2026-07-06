# Reverse Engineering

<!-- encoding: utf-8 -->

Process for extracting knowledge from vendor JS bundles, API responses, and legacy code.

Covers: re-engineering cycle, common sources, design documentation. Does not cover: development workflow, testing methodology.

## Re-engineering cycle

1. **Extract** вЂ” read JS bundle / API trace / server response / legacy code
1. **Decide** вЂ” write architecture decision in `doc/ARCHITECTURE.md` в†’ Design Decisions
1. **Design** вЂ” plan the implementation
1. **Write tests** from design specs
1. **Implement** until tests pass
1. **Violation** вЂ” if any step was skipped в†’ `TODO.md` Backlog entry в†’ must-fix before next feature

This cycle is mandatory before every reverse-engineering-derived feature.

## Common sources

- Vendor JS bundles in `src/static/assets/libs/`
- API responses from the deployed site
- Legacy Flask view functions with no tests
- HTML structure of existing pages

## Future skill

This document provides the basis for a future `.skills/reverse-engineering/README.md` skill.
