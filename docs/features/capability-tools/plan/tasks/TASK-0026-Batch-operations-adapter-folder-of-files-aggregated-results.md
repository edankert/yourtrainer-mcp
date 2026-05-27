---
type: "[[task]]"
id: TASK-0026
aliases: ["TASK-0026"]
title: "Batch operations adapter (folder-of-files → aggregated results)"
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

# TASK-0026 — Batch operations adapter (folder-of-files → aggregated results)

Tool that takes a folder of workouts or activities and runs another capability tool against all of them, returning aggregated results. Examples: convert a library of 50 ZWO files to FIT-workout; compute fitness curve from a season's worth of activities; run the linter against every workout in a library and emit a summary report.

## Acceptance
- [ ] Tool takes: input folder path (as a base64-zipped upload), target capability tool, args.
- [ ] Returns: aggregated results as JSON + (where relevant) output files as a base64-zipped download.
- [ ] Handles ≥100 files without memory blow-up.
- [ ] Per-file errors don't abort the batch; reported in the aggregated result.
