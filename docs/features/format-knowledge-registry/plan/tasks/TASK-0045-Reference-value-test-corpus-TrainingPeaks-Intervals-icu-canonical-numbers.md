---
type: "[[task]]"
id: TASK-0045
aliases: ["TASK-0045"]
title: "Reference-value test corpus (TrainingPeaks / Intervals.icu canonical numbers)"
status: backlog
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-27
source: []
implements: ["[[FEAT-0001]]"]
fixes: []
effort: M
---

# TASK-0045 — Reference-value test corpus (TrainingPeaks / Intervals.icu canonical numbers)

Curate a corpus of canonical activities with known reference values from authoritative third-party tools (TrainingPeaks, Intervals.icu, WKO5). Codify as test fixtures the math tools (NP, IF, TSS, CTL/ATL/TSB, peak power) assert against. Without this corpus, the math validation acceptance criteria in TASK-0021 / TASK-0022 / TASK-0027 / TASK-0028 are unimplementable. Optional / QoL — could be folded into each math task's acceptance work, but centralising it avoids per-task curation effort.

## Acceptance
- [ ] ≥10 canonical activities with reference values from at least 2 authoritative tools per activity.
- [ ] Per-activity reference manifest: `{activity_id, source_tool, source_version, reference_values: {np, if, tss, ...}, captured_date}`.
- [ ] Tolerance documented per metric (NP within ±2% across tools is standard; IF/TSS exact given consistent FTP).
- [ ] Test fixtures wired into TASK-0021, TASK-0022, TASK-0027, TASK-0028 acceptance.
- [ ] Process documented for adding new reference activities (any contributor can extend the corpus).
