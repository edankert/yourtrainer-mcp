---
type: "[[task]]"
id: TASK-0032
aliases: ["TASK-0032"]
title: "Format-conversion roundtrip test harness (LLM self-correction tool)"
status: backlog
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-27
source: []
implements: ["[[FEAT-0005]]"]
fixes: []
effort: M
---

# TASK-0032 — Format-conversion roundtrip test harness (LLM self-correction tool)

Given an original file in format X and a converted file in format Y (the LLM's output), the tool re-converts Y back to X using deterministic reference parsers and compares to the original. Returns a structured loss report: what was preserved, what changed, what was lost. Lets agents self-correct their conversions without humans in the loop. Stateless.

## Acceptance
- [ ] Roundtrip works for: ZWO ⟷ ERG, ZWO ⟷ FIT-workout, GPX ⟷ TCX (using the FEAT-0001 reference parsers — not our own converters).
- [ ] Loss report structured: `{preserved: [...], changed: [{field, before, after}], lost: [...]}`.
- [ ] Tested against canonical samples where intentional loss is expected (e.g. ZWO → ERG drops text events; should be reported, not flagged as a bug).
- [ ] LLM can use the report to retry conversion — manual end-to-end test: LLM converts, harness reports issues, LLM retries, harness re-validates.
- [ ] Stateless: both files in, diff out, nothing retained.
