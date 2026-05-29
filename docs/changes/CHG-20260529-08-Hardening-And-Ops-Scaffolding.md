---
type: "[[change]]"
id: CHG-20260529-08
title: "Hardening (property/golden/perf) + ops scaffolding (monitoring/status)"
status: merged
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: []
commit: ""
pr: ""
impacts: ["tests", "ci", "ops", "deploy"]
issues: []
features: ["[[FEAT-0001]]", "[[FEAT-0002]]"]
related: ["[[TASK-0041]]", "[[TASK-0044]]", "[[TASK-0011]]", "[[TASK-0043]]", "[[TST-0009]]"]
---

# Hardening + ops scaffolding (Wave 7)

## Summary
Hardening and the host-independent half of the hosting tasks:
- **TASK-0041 (done):** Hypothesis property tests (`tests/test_properties.py`)
  for power-math and workout/FIT roundtrip invariants; golden-file regression
  locks (`tests/golden/` + `tests/test_golden.py`); added `hypothesis` to dev
  deps. Property testing surfaced (and we fixed) three over-strict assumptions.
- **TASK-0044 (done):** performance budget tests (`tests/test_performance.py`,
  guards against O(n²)) + `scripts/benchmark.py` baseline reporter.
- **TASK-0011 (doing):** `deploy/healthcheck.sh` liveness probe + `get_health`
  metrics + alerting wiring guide. Verified locally (exit 0 up / 1 down).
- **TASK-0043 (doing):** `deploy/status/canary.py` + static `index.html` status
  page. Verified locally (writes status.json with latency).

## Documentation Coverage (All Types Considered)
- features: updated (FEAT-0001 test-infra complete; FEAT-0002 ops artefacts)
- requirements: not-applicable
- tasks: updated (TASK-0041/0044 → done; TASK-0011/0043 → doing)
- issues: not-applicable
- tests: new (TST-0009)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (statuses, counters, metrics, active_wave)

## Verification
- `pytest -q` → 137 passed. ruff + mypy clean.
- Ops scripts exercised against a live local server: healthcheck OK/FAIL,
  canary writes status.json (latency ~15 ms).

## Follow-ups (remaining for full PHASE-001 exit)
- [ ] Live VPS deploy (held per user) → then TASK-0009 provisioning, and
  TASK-0011/0043 flip to done once the alert channel + status page are hosted.
- [ ] External-asset tasks: TASK-0020 real FIT samples + device test,
  TASK-0045 / TASK-0021 TrainingPeaks reference corpus.
