---
type: "[[task]]"
id: TASK-0051
aliases: ["TASK-0051"]
title: "Recovery time estimator"
status: done
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-29
source: []
implements: ["[[FEAT-0004]]"]
fixes: []
effort: S
---

> **Done 2026-05-29 (CHG-20260529-04, [[TST-0004]]).** training_load.recovery_estimate — TSS → strain band + recovery hours (heuristic).

# TASK-0051 — Recovery time estimator

Given an activity's TSS + recent training-load context (last 14 days of CTL / ATL from TASK-0027) → estimate hours-until-recovered. Used for planning the next workout. Composable; no new math primitive — just packaged for the *"can I ride hard tomorrow?"* question.

## Acceptance
- [ ] Composes activity TSS (TASK-0021) + training-load curve (TASK-0027) → recovery hours.
- [ ] Documented model (e.g. ATL decay rate + TSS proportional load).
- [ ] Returns: `{recovery_hours, baseline_atl, current_atl_estimate, confidence, explanation}`.
- [ ] Stateless.
