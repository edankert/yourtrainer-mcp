---
type: "[[task]]"
id: TASK-0027
aliases: ["TASK-0027"]
title: "Training-load curve (CTL / ATL / TSB) from a folder of activities"
status: backlog
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-27
source: []
implements: ["[[FEAT-0004]]"]
fixes: []
effort: M
---

# TASK-0027 — Training-load curve (CTL / ATL / TSB) from a folder of activities

Given a folder of activity files (FIT/TCX/GPX) + the rider's FTP, compute the training-load curve. CTL = 42-day exponentially-weighted moving average of daily TSS (chronic / fitness). ATL = 7-day EWMA (acute / fatigue). TSB = CTL − ATL (form / readiness). Output: time series of `(date, ctl, atl, tsb, daily_tss)` rows. Stateless: the folder is passed in, computation runs, results returned, no inputs retained.

## Acceptance
- [ ] Computes CTL / ATL / TSB correctly per the canonical Coggan formulas.
- [ ] Output validated against reference values from TrainingPeaks / Intervals.icu for ≥3 canonical multi-week activity samples.
- [ ] Handles ≥365 days of activities without memory blow-up.
- [ ] Returns metadata: number of activity days, gaps, range covered.
- [ ] Stateless: no input data retained beyond the call.
