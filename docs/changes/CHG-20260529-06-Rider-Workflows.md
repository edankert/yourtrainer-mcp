---
type: "[[change]]"
id: CHG-20260529-06
title: "Rider workflows: pacing, climbs, anonymise, adherence, migration, roundtrip (Wave 5)"
status: merged
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: []
commit: ""
pr: ""
impacts: ["rider-workflows", "mcp-server"]
issues: []
features: ["[[FEAT-0005]]"]
related: ["[[TASK-0029]]", "[[TASK-0030]]", "[[TASK-0031]]", "[[TASK-0032]]", "[[TASK-0034]]", "[[TASK-0048]]", "[[TST-0006]]"]
---

# Rider workflows (Wave 5)

## Summary
Implemented FEAT-0005 in full:
- `route.py` — route profile, climb detection + categorisation (TASK-0048),
  gradient-aware pacing strategy (TASK-0029).
- `anonymize.py` — GPX privacy-zone removal + optional HR strip (TASK-0030).
- `adherence.py` — plan-vs-actual scorecard (TASK-0034).
- `workflows.py` — migration inventory (TASK-0031) + conversion roundtrip
  harness (TASK-0032).

MCP tools: `analyze_route`, `anonymize_gpx`, `adherence_scorecard`,
`migration_inventory`, `roundtrip_workout`.

## Impact
- FEAT-0005 is complete; the MCP now exposes ~30 tools across knowledge +
  capability + workflow layers.

## Documentation Coverage (All Types Considered)
- features: updated (FEAT-0005 → done)
- requirements: not-applicable
- tasks: updated (TASK-0029/0030/0031/0032/0034/0048 → done)
- issues: not-applicable
- tests: new (TST-0006)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (statuses, FEAT-0005 done, counters, metrics, focus → Wave 6)

## Verification
- `pytest -q` → 107 passed. ruff + mypy clean.

## Follow-ups
- [ ] Wave 6: library ops (FEAT-0006) + close hosting/trojan-horse.
- [ ] Anonymisation currently covers GPX; TCX/FIT users convert to GPX first
  (a future enhancement could anonymise those in place).
