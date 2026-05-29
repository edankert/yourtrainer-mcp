---
type: "[[task]]"
id: TASK-0039
aliases: ["TASK-0039"]
title: "Library deduplication — find near-duplicate workouts"
status: done
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-29
source: []
implements: ["[[FEAT-0006]]"]
fixes: []
effort: M
---

> **Done 2026-05-29 (CHG-20260529-07).** library.find_duplicates — near-duplicate workouts by per-second power-series comparison.

# TASK-0039 — Library deduplication — find near-duplicate workouts

Given a library (or index from TASK-0038) + a similarity threshold, return a dedup report: groups of near-identical workouts. Useful after library migration when riders accumulate duplicates from multiple imports.

## Acceptance
- [ ] Similarity measure: structured-intent comparison (via TASK-0033 decompose) with configurable target-tolerance and duration-tolerance.
- [ ] Output: `[{group_id, members: [paths], similarity, suggested_keeper}]`.
- [ ] Configurable threshold (default: 0.95 = near-identical).
- [ ] Stateless.
