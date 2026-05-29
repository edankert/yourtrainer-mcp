---
type: "[[task]]"
id: TASK-0046
aliases: ["TASK-0046"]
title: "FTP detection from a ride"
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

> **Done 2026-05-29 (CHG-20260529-04, [[TST-0004]]).** analysis.estimate_ftp — best 60-min, else 95% of best 20-min.

# TASK-0046 — FTP detection from a ride

Tool that analyses an activity file and estimates the rider's FTP. Several documented detection methods, selected automatically based on ride shape (or specified explicitly):
- 20-min sustained effort × 0.95 (classic Coggan)
- 8-min sustained effort × 0.90 (legacy TR-style)
- Ramp test (last-minute average × 0.75)
- Best 60-min average from a long free-ride (CP model proxy)

Returns: estimated_ftp, method_used, evidence (effort start/end timestamps), confidence. The rider doesn't need to have done a formal test — the tool surfaces the best estimate available from whatever activity is provided.

## Acceptance
- [ ] All 4 detection methods implemented; auto-selection logic documented.
- [ ] Returns structured result: `{estimated_ftp, method_used, evidence: [{start, end, avg_power}], confidence}`.
- [ ] Validated against canonical activities with known FTP (cross-checked against TR/Intervals.icu values).
- [ ] Edge cases: ride too short → returns `null` with reason; activity without power → returns `null` with reason.
- [ ] Stateless.
