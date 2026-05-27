---
type: "[[task]]"
id: TASK-0007
aliases: ["TASK-0007"]
title: "Author locale string-bundle format documentation (Android XML / iOS strings / .po / flat JSON)"
status: backlog
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-27
source: []
implements: ["[[FEAT-0001]]"]
fixes: []
effort: M
---

# TASK-0007 — Author locale string-bundle format documentation (Android XML / iOS strings / .po / flat JSON)

Document the four locale formats that indie cycling apps share. Cover: key structure, plural-form support, comment conventions, escaping rules. Per-format `constraints.json` covers which apps/build-systems prefer which dialect.

## Acceptance
- [ ] `specs/locale-bundle/<format>.md` for all four formats.
- [ ] ≥2 canonical examples per format from real cycling-app translation bundles.
- [ ] Conversion notes for the practical pairs.
