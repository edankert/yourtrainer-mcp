---
type: "[[task]]"
id: TASK-0034
aliases: ["TASK-0034"]
title: "Plan-vs-actual adherence scorecard"
status: backlog
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-27
source: []
implements: ["[[FEAT-0005]]"]
fixes: []
effort: L
---

# TASK-0034 — Plan-vs-actual adherence scorecard

Tool that takes a workout file (the plan) + an activity file (the executed ride) + the rider's FTP and returns a per-interval adherence scorecard. Closes the planning-execution loop. Pairs naturally with upstream FEAT-0084 (AI Coach as Training Partner) — the AI handles RPE / subjective feedback; this tool handles objective per-interval scoring deterministically. Without it, the comparison is left to the LLM, which is exactly the kind of multi-time-series analysis LLMs do badly.

## Acceptance
- [ ] Tool aligns workout intervals to the executed time-series (timestamp-based or sequence-based depending on activity metadata).
- [ ] Per-interval output: `{interval_id, target, actual_avg, actual_peak, adherence_pct, drift, cadence_avg, hr_avg, notes}`.
- [ ] Whole-workout summary: overall adherence %, count of intervals nailed (>95%), count missed (<85%), count exceeded (>110%), drift trend across the session.
- [ ] Handles edge cases: dropped intervals (rider quit mid-workout), exceeded intervals, mis-aligned start (rider hit START late), free-ride segments that have no plan target.
- [ ] Validated against ≥5 canonical plan+activity pairs with known scorecard outcomes (from upstream Your Trainer test fixtures).
- [ ] Stateless.
