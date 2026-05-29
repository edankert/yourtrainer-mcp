---
type: "[[task]]"
id: TASK-0024
aliases: ["TASK-0024"]
title: "App-acceptance checker (consumes FEAT-0001 constraints catalogue)"
status: done
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-29
source: []
implements: ["[[FEAT-0004]]"]
fixes: []
effort: M
---

> **Done 2026-05-29 (CHG-20260529-02, [[TST-0002]]).** app_acceptance_check with a v1 constraints seed (zwift/garmin_edge/wahoo); authoritative catalogue arrives with FEAT-0001.

# TASK-0024 — App-acceptance checker (consumes FEAT-0001 constraints catalogue)

Given a workout file, returns a structured report: which apps load it cleanly, which need conversion, which reject it. Backed by the per-app constraints catalogue from FEAT-0001 TASK-0002 / TASK-0004.

## Acceptance
- [ ] Reads workout file (ZWO, FIT-workout, ERG/MRC, `.ytw`).
- [ ] Consults FEAT-0001 constraints catalogue.
- [ ] Returns structured `{app: status, reason}` map for ≥5 apps.
- [ ] Surfaces specific violations (`text event 'Recovery 10:00' exceeds Garmin Edge 530 32-char limit`).
