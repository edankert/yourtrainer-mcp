---
type: "[[issue]]"
id: ISS-0001
title: ".ytw writer schema does not match the real Your Trainer .ytw format"
status: triage
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
severity: high
related: ["[[FEAT-0004]]", "[[FEAT-0007]]", "[[TASK-0023]]", "[[TASK-0006]]"]
---

# ISS-0001 — .ytw writer schema mismatch

## Problem
`build_workout_from_intent(output_format="ytw")` (and `workout.to_ytw`) emit a
**simplified** schema: `{"format": "ytw", "version": 1, "name", "steps": [...]}`.

The **real** Your Trainer `.ytw` files in the website library use a different,
richer schema — observed keys include `programId`, `programName`, `description`,
structured intervals/segments, and **localized cue strings** (e.g. per-locale
`ss:2`, `cooldown:0` messages across all Tier-1 locales).

Discovered while wiring FEAT-0007 (a real library `.ytw` failed the assumed
shape). Our `.ytw` was defined speculatively (noted at the time in ADR-0004 /
TASK-0006).

## Impact
- `.ytw` produced by the MCP **will not import cleanly into Your Trainer** until
  reconciled. This blocks the workout-creation integration's "AI builds a .ytw"
  path (the very flow in docs/INTEGRATION.md, Flow 1/2).

## Resolution options
1. Update `to_ytw` to emit the real Your Trainer `.ytw` schema (preferred) —
   needs the authoritative `.ytw` spec / `workout-intent.json` schema from the
   website (`public/schemas/workout-intent.json` exists — start there).
2. Update `specs/ytw.json` to document the real format.
3. Add a converter from our intent model → real `.ytw` (incl. cue localization?).

## Next step
Pull the canonical `.ytw` / `workout-intent.json` schema and realign the writer +
the `specs/ytw.json` doc. Needs a decision on cue-string localization scope.
