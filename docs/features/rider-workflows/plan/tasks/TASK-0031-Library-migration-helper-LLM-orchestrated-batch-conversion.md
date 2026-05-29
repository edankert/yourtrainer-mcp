---
type: "[[task]]"
id: TASK-0031
aliases: ["TASK-0031"]
title: "Library migration helper (LLM-orchestrated batch conversion)"
status: done
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-29
source: []
implements: ["[[FEAT-0005]]"]
fixes: []
effort: M
---

> **Done 2026-05-29 (CHG-20260529-06, [[TST-0006]]).** workflows.migration_inventory — detects/groups files, flags workouts needing conversion to target; LLM does the conversion.

# TASK-0031 — Library migration helper (LLM-orchestrated batch conversion)

Helper that prepares a structured migration plan for converting a library of workouts from app X to app Y. Tool returns: per-file conversion metadata, target-format spec references (from FEAT-0001 knowledge registry), validation hooks. The LLM does the actual conversion using the registry's reference material; tool validates each output via FEAT-0001 validators; FEAT-0004 batch ops aggregates results. Stateless on the MCP side — the LLM client orchestrates iteration.

## Acceptance
- [ ] Tool returns structured per-file conversion plan with: source format, target format, reference spec excerpt, validator function.
- [ ] Plan composable with FEAT-0004 batch ops + FEAT-0001 validators.
- [ ] Manual end-to-end test: LLM orchestrates conversion of 10 TrainerRoad ERG files → 10 valid Zwift ZWO files.
- [ ] Per-file errors surfaced in the result; batch doesn't abort on partial failure.
- [ ] Stateless: the plan is generated, returned, and discarded — no progress state held server-side.
