---
type: "[[task]]"
id: TASK-0028
aliases: ["TASK-0028"]
title: "HR–power decoupling calculator (endurance-ride pace quality)"
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

> **Done 2026-05-29 (CHG-20260529-04, [[TST-0004]]).** analysis.hr_power_decoupling — Pw:Hr efficiency-factor drift across ride halves; <5% well-paced flag.

# TASK-0028 — HR–power decoupling calculator (endurance-ride pace quality)

Given a single endurance activity file (FIT/TCX), compute HR–power decoupling. Standard formula: (Pw:Hr ratio first-half) vs (Pw:Hr ratio second-half), reported as % drift. Conventional thresholds: <5% aerobic; 5–10% moderate decoupling; >10% poor pace quality. Lets the LLM answer 'was this a quality endurance ride?' with grounding rather than hand-waving.

## Acceptance
- [ ] Computes decoupling % per the canonical Friel / Allen-Coggan formula.
- [ ] Validated against reference values for canonical activities.
- [ ] Returns the threshold band (aerobic / moderate / poor) for easy LLM consumption.
- [ ] Returns `null` with a `reason` field if the activity is too short or fails quality checks (no HR stream, intervals not steady).
- [ ] Stateless.
