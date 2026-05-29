---
type: "[[task]]"
id: TASK-0053
aliases: ["TASK-0053"]
title: "HR drift / aerobic threshold estimator (MAF-style)"
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

> **Done 2026-05-29 (CHG-20260529-04, [[TST-0004]]).** analysis.hr_drift — half-split HR drift % + indicative aerobic-HR estimate (MAF-style; approximate).

# TASK-0053 — HR drift / aerobic threshold estimator (MAF-style)

Given a steady-state endurance activity (long ride, mostly Z1–Z2), compute HR drift % over the duration (first-half vs second-half mean HR at equivalent power), estimate aerobic threshold from Pa:Hr decoupling pattern. Useful for MAF / aerobic-base training. Distinct from TASK-0028 (HR–power decoupling) — that's a pace-quality metric; this is a threshold-estimation metric.

## Acceptance
- [ ] Detects whether the activity qualifies as steady-state (HR/power consistency); returns null with reason if not.
- [ ] Computes drift % per documented formula.
- [ ] Estimates aerobic threshold ± confidence band from the decoupling pattern.
- [ ] Validated against MAF training references for canonical rides.
- [ ] Stateless.
