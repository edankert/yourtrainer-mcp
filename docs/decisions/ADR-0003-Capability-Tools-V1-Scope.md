---
type: "[[adr]]"
id: ADR-0003
title: "Capability tools v1 scope (in/out + deferral list)"
status: accepted
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: ["[[TASK-0019]]"]
decision: "v1 capability surface = FIT/TCX/GPX read, NP/IF/TSS + activity inspector, peak-power curve, workout build-from-intent, workout decompose, workout scale, structure linter, app-acceptance checker, batch adapter. Deferred: Strava OAuth, BLE push, vision-language pre-processor, OAuth-mediated integrations."
context: "FEAT-0004 needs a locked v1 surface so the build has a finish line and statelessness is preserved."
alternatives: ["Ship everything in FEAT-0004 at once", "Defer all math to a later phase"]
consequences: ["Clear v1 finish line.", "Stateless-only tools; nothing needing tokens/accounts ships in v1.", "Deferred items have a documented future-phase home."]
supersedes: ""
superseded: ""
related: ["[[TASK-0019]]", "[[FEAT-0004]]", "[[PHASE-001-Initial-Launch]]"]
---

# Capability tools v1 scope

## Context
FEAT-0004 lists ~25 candidate tools. Shipping all at once has no finish line, and some candidates (Strava pull, BLE push) violate the strict-statelessness invariant. This ADR locks the v1 surface and records the deferral list with rationale.

## Decision

**In v1 (all stateless, file-in → result-out):**
- File reading: FIT (optional `fitparse` extra), TCX, GPX activity files; lightweight format detection.
- Activity inspector → JSON summary: duration, distance, elevation gain, avg/peak power, **NP / IF / TSS**, avg/peak HR, avg/peak cadence, avg speed, time-in-zone.
- Peak power curve (mean-max 1s/5s/30s/1min/5min/20min/60min).
- Workout build-from-intent (`{warmup, intervals, cooldown}` → ZWO + FIT + `.ytw`).
- Workout decompose (file → structured intent) and workout scale (duration / FTP / intensity).
- Workout structure linter; app-acceptance checker; batch operations adapter.

**Deferred (with future-phase home):**
- **Strava OAuth pull / Garmin Connect / TrainingPeaks API** — require state (tokens/refresh/callbacks); violate statelessness. Home: a separate stateful service, not PHASE-001. User flow stays export-then-upload.
- **BLE direct push** to bike computers — requires a stateful device session; out of a stateless HTTP MCP.
- **Vision-language pre-processor** (screenshot → workout) — lives app-side (upstream FEAT-0086 TASK-0618), not in this MCP.

## Alternatives
- **Ship all of FEAT-0004 at once** — no finish line; risks pulling in stateful tools.
- **Defer all math** — removes the most LLM-valuable, genuinely-tool-required capability; rejected.

## Consequences
- v1 has a concrete, testable surface.
- The statelessness invariant is preserved by construction — no v1 tool needs an account or token.
- This session lands the first slice: the activity inspector + NP/IF/TSS engine (TASK-0021). Remaining v1 tools follow as their own tasks.
