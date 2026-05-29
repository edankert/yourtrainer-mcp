---
type: "[[change]]"
id: CHG-20260529-09
title: "Public docs-site mirror generator + OSS contribution docs (Wave 8)"
status: merged
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: []
commit: ""
pr: ""
impacts: ["knowledge-registry", "docs", "oss"]
issues: []
features: ["[[FEAT-0001]]", "[[FEAT-0003]]"]
related: ["[[TASK-0055]]", "[[TASK-0018]]", "[[TST-0010]]", "[[ADR-0002]]"]
---

# Public docs-site mirror + OSS contribution docs (Wave 8)

## Summary
Polish wave (host-independent):
- **TASK-0055 (done):** `docs_site.build_site` + `scripts/build_docs.py` render
  the packaged `specs/` corpus to a dependency-free static HTML site (index +
  one page per format, 10 pages). Examples HTML-escaped, attribution footer, no
  comparative content. Output goes to `build/docs-site/` (gitignored); hosting
  is a deploy step. Satisfies the FEAT-0001 "public docs site mirror" exit item.
- **OSS docs:** added `CONTRIBUTING.md` and `MAINTAINERS.md` — the ADR-0002 /
  TASK-0018 follow-up (contribution expectations, scope, statelessness +
  no-comparative-content ground rules, RISK-0002 maintenance posture).
- Added a CI badge to the README.

## Documentation Coverage (All Types Considered)
- features: updated (FEAT-0001 docs-site mirror delivered)
- requirements: not-applicable
- tasks: updated (TASK-0055 → done; closes the TASK-0018 MAINTAINERS follow-up)
- issues: not-applicable
- tests: new (TST-0010)
- workflows: not-applicable
- decisions: not-applicable (covered by ADR-0002)
- risks: RISK-0002 — MAINTAINERS.md now records the maintenance posture
- changes: new (this note)
- snapshot: updated (TASK counter 54→55, statuses, metrics, focus)

## Verification
- `pytest -q` → 142 passed. ruff + mypy clean.
- `python scripts/build_docs.py` → 10 pages in build/docs-site/.

## Follow-ups
- [ ] Host the generated site (e.g. cycling-formats.your-applications.com) —
  a deploy step alongside the MCP server.
