---
type: "[[task]]"
id: TASK-0038
aliases: ["TASK-0038"]
title: "Library indexing — build searchable metadata index from a folder"
status: backlog
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-27
source: []
implements: ["[[FEAT-0006]]"]
fixes: []
effort: M
---

# TASK-0038 — Library indexing — build searchable metadata index from a folder

Given a folder of workouts or activities, build a searchable metadata index: per-file metadata (format, type, duration, primary metric, brief signature) without doing full analysis. Useful for: large library navigation, search, downstream filter operations.

## Acceptance
- [ ] Indexes folders of ≥500 mixed-format files in under 30s.
- [ ] Per-file index entry: `{path, format, type, duration_s, summary, signature_hash}`.
- [ ] Index is JSON; consumable by downstream library ops (TASK-0039, TASK-0040) and by the agent for filtering.
- [ ] Stateless.
