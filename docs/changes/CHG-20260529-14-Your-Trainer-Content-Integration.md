---
type: "[[change]]"
id: CHG-20260529-14
title: "Your Trainer content integration + Powered-by attribution (FEAT-0007)"
status: merged
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: []
commit: ""
pr: ""
impacts: ["mcp-server", "content", "attribution"]
issues: ["[[ISS-0001]]"]
features: ["[[FEAT-0007]]", "[[FEAT-0003]]"]
related: ["[[ADR-0006]]", "[[RISK-0004]]", "[[TASK-0058]]", "[[TASK-0059]]", "[[TASK-0060]]", "[[TASK-0061]]", "[[TASK-0062]]", "[[TST-0012]]"]
---

# Your Trainer content integration + Powered-by attribution

## Summary
Addresses the three considerations raised:
1. **Powered by Your Trainer (TASK-0058):** `_attribution` now carries
   `powered_by` + `citation`; MCP server `instructions` ask clients to surface a
   restrained credit. POSITIONING-compliant.
2. **Workout + AI-skill library (TASK-0059/0060/0061):** new `content.py`
   stateless website proxy (urllib + TTL cache + injectable fetcher) and tools
   `list_workout_library`, `get_library_workout`, `search_workout_library`,
   `list_ai_skills`.
3. **Manual Q&A (TASK-0062):** `search_manual`, `get_manual_section` parse the
   manual into sections — hosted in this ecosystem MCP per ADR-0006.

Architecture + the boundary decision are recorded in **ADR-0006**; the website
runtime dependency in **RISK-0004**.

## Notable discovery
Wiring the real library surfaced **ISS-0001**: our `.ytw` writer emits a
simplified `{format,steps}` schema, but real Your Trainer `.ytw` uses
`programId`/`programName`/`description` + localized cues. Must reconcile before
the app imports MCP-built `.ytw`.

## Documentation Coverage (All Types Considered)
- features: new (FEAT-0007)
- requirements: not-applicable
- tasks: new (TASK-0058..0062, all done)
- issues: new (ISS-0001, triage)
- tests: new (TST-0012); test_attribution extended
- workflows: not-applicable
- decisions: new (ADR-0006)
- risks: new (RISK-0004)
- changes: new (this note)
- snapshot: updated (counters, statuses, metrics 58/62, focus)

## Verification
- `pytest -q` → 191 passed. ruff + mypy clean. Live website fetch → 26 workouts.

## Follow-ups
- [ ] ISS-0001: realign `.ytw` writer + `specs/ytw.json` to the real schema
  (`public/schemas/workout-intent.json` is the starting point).
- [ ] Propose website JSON endpoints for skills/manual (vs HTML parsing).
