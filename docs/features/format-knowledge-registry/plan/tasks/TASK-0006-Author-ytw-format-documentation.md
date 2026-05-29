---
type: "[[task]]"
id: TASK-0006
aliases: ["TASK-0006"]
title: "Author .ytw format documentation"
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

> **Done 2026-05-29 (CHG-20260529-05, [[TST-0005]]).** specs/ytw.json: the .ytw JSON format v1 documented (matches workout.py); examples + conversion notes; validate('ytw').

# TASK-0006 — Author .ytw format documentation

Document Your Trainer's own `.ytw` workout format as a first-class entry in the registry. Spec, ≥3 canonical examples, conversion notes to/from ZWO and FIT-workout. This is also the moment to publish the `.ytw` spec authoritatively for the first time (it has been internal until now).

## Acceptance
- [ ] `specs/ytw/spec.md` covers the full schema with examples.
- [ ] ≥3 canonical `.ytw` example files (sweet-spot, V02 max, free-ride).
- [ ] Conversion notes for `.ytw` ⟷ ZWO and `.ytw` ⟷ FIT-workout.
- [ ] Cross-link from `your-applications.com/your-trainer/workout-schema.html` to the registry entry as the canonical source.
