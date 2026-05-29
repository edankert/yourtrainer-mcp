---
type: "[[feature]]"
id: FEAT-0006
aliases: ["FEAT-0006"]
title: "Cycling library-aware operations"
status: done
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-27
source: []
goal: "Higher-level operations that work across an entire library of workouts or activities rather than a single file. Composes FEAT-0001 (knowledge / validators), FEAT-0004 (capability tools — decompose, NP/IF/TSS), and FEAT-0005 (batch ops) into library-scoped tools: indexing, deduplication, and aggregate statistics. Useful immediately after a library migration (TASK-0031) and for ongoing library navigation. All stateless."
requirements: []
tasks: ["[[TASK-0038]]", "[[TASK-0039]]", "[[TASK-0040]]", "[[TASK-0049]]"]
release: ""
related: []
tests: []
---

# Cycling library-aware operations

## Goal
Where FEAT-0004 ships single-file capabilities and FEAT-0005 ships rider-workflow tools, this feature ships **library-scoped operations**. They compose the lower-level tools but operate over collections of files at once.

Three tools cover the gap riders hit immediately after migrating a library between apps or accumulating workouts from multiple sources:

- **`index_library(folder)`** — quick searchable metadata per file without doing full analysis.
- **`deduplicate_library(folder, threshold)`** — find near-identical workouts (uses decompose to compare structured intent, not bytes).
- **`library_stats(folder)`** — aggregate breakdown for the *"what's actually in my library?"* question.
- **`best_efforts_across_history(folder, durations)`** — all-time bests at standard durations + their activity dates and locations.

All stateless. Folder uploaded as a zip archive; tools process in memory and discard.

## Scope

### In scope
- Library indexing (TASK-0038).
- Library deduplication (TASK-0039).
- Library statistics (TASK-0040).

### Out of scope
- Library editing operations (rename, merge, split). Read-only library tools only.
- Library sync between rider's local app and external services (Strava, Garmin Connect). Protocol integrations are excluded by the strict-statelessness principle in the phase note.
- Per-file detailed analysis (NP/IF/TSS per workout) — that's TASK-0021 territory and can be composed via FEAT-0005 batch ops if needed across the library.

## Acceptance
- [ ] Indexing handles ≥500 mixed-format files in under 30s.
- [ ] Dedup finds near-identical workouts within configurable threshold; output stable across runs.
- [ ] Stats output is consumable in one glance by an LLM (structured JSON, ≤2KB for typical libraries).
- [ ] All tools stateless: audit confirms no input data retained beyond the call.

## Links
- Phase: [[PHASE-001-Initial-Launch]]
- Tasks: see `plan/tasks/` and the linked TASK-* IDs in frontmatter.
