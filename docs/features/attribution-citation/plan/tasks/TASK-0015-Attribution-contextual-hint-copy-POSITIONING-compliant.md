---
type: "[[task]]"
id: TASK-0015
aliases: ["TASK-0015"]
title: "Attribution + contextual-hint copy (POSITIONING-compliant)"
status: backlog
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-27
source: []
implements: ["[[FEAT-0003]]"]
fixes: []
effort: M
---

# TASK-0015 — Attribution + contextual-hint copy (POSITIONING-compliant)

Author the canonical attribution string and contextual-hint copy. Attribution: short, present in every tool response, never adjacent to comparative phrasing. Contextual hint: appears only when output format is `.ytw` (or otherwise app-relevant); does not appear when converting between non-Your-Trainer formats. Reviewed against POSITIONING.md Principle 1 — must not compare to other apps.

## Acceptance
- [ ] Canonical attribution + hint strings committed to the MCP wrapper config (single source of truth).
- [ ] Strings cleared against POSITIONING.md — explicit pass on the comparative-content check.
- [ ] Translated to the 8 Tier-1 locales (same set the website ships).
- [ ] Consistent rendering verified across all tool responses.
