---
type: "[[task]]"
id: TASK-0007
aliases: ["TASK-0007"]
title: "Author locale string-bundle format documentation (Android XML / iOS strings / .po / flat JSON)"
status: done
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-29
source: []
implements: ["[[FEAT-0001]]"]
fixes: []
effort: M
---

> **Done 2026-05-29 (CHG-20260529-05, [[TST-0005]]).** specs/locale.json: Android strings.xml / iOS .strings / gettext .po / flat JSON with examples, escaping & plural/placeholder constraints.

# TASK-0007 — Author locale string-bundle format documentation (Android XML / iOS strings / .po / flat JSON)

Document the four locale formats that indie cycling apps share. Cover: key structure, plural-form support, comment conventions, escaping rules. Per-format `constraints.json` covers which apps/build-systems prefer which dialect.

## Acceptance
- [ ] `specs/locale-bundle/<format>.md` for all four formats.
- [ ] ≥2 canonical examples per format from real cycling-app translation bundles.
- [ ] Conversion notes for the practical pairs.
