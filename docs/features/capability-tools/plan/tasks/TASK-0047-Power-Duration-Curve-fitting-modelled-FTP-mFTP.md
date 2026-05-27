---
type: "[[task]]"
id: TASK-0047
aliases: ["TASK-0047"]
title: "Power Duration Curve fitting + modelled FTP (mFTP)"
status: backlog
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-27
source: []
implements: ["[[FEAT-0004]]"]
fixes: []
effort: L
---

# TASK-0047 — Power Duration Curve fitting + modelled FTP (mFTP)

Fit a power-duration curve across a folder of activities and extract: modelled FTP (mFTP), critical power (CP), W' (anaerobic work capacity), stamina (fatigue resistance). This is the analytical capability WKO5 charges $150 for; pure math on the rider's data.

Returns: per-duration peak power (1s / 5s / 30s / 1min / 5min / 20min / 60min), fitted curve parameters, model fit quality (R²), recommended testing efforts to improve fit confidence.

## Acceptance
- [ ] Mean-max curve computed across folder; peaks extracted at standard durations.
- [ ] CP / W' fitted via published 2-parameter or 3-parameter Monod/Skiba model (selectable).
- [ ] Output includes fit quality + recommended efforts to fill gaps in the curve.
- [ ] Validated against WKO5 / Intervals.icu reference outputs for canonical seasons.
- [ ] Handles ≥6 months of activity data without memory blow-up.
- [ ] Stateless.
