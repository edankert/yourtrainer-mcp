---
type: "[[task]]"
id: TASK-0055
aliases: ["TASK-0055"]
title: "Public docs-site mirror generator (renders specs/ corpus to static HTML)"
status: done
phase: "[[PHASE-001-Initial-Launch]]"
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: []
implements: ["[[FEAT-0001]]"]
fixes: []
effort: M
---

# TASK-0055 — Public docs-site mirror generator

Render the `specs/` knowledge corpus to a static, dependency-free HTML site so
the same source of truth serves both LLM clients (via MCP) and human readers
(the public docs-site mirror named in the PHASE-001 exit criteria). This is the
human-facing half of the trojan-horse citation strategy.

## Acceptance
- [x] A generator script renders every format to a static HTML page (spec,
  examples, constraints, conversion notes, glossary, version) + an index.
- [x] Output is dependency-free static HTML; examples are HTML-escaped.
- [x] POSITIONING-compliant: attribution present, no comparative content.
- [x] Covered by a test that builds the site and asserts structure.
- [x] Generated into `build/` (not committed); hosting is a deploy step.

> **Done 2026-05-29 (CHG-20260529-09, [[TST-0010]]).** `docs_site.build_site` +
> `scripts/build_docs.py` render the 9-format corpus + index to static HTML
> (10 pages); examples HTML-escaped; attribution footer; no comparative content.
