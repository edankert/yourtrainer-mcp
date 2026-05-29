---
type: "[[task]]"
id: TASK-0044
aliases: ["TASK-0044"]
title: "Performance baselines + regression detection"
status: done
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-29
source: []
implements: ["[[FEAT-0002]]"]
fixes: []
effort: S
---

> **Done 2026-05-29 (CHG-20260529-08).** tests/test_performance.py budget tests (catch O(n^2)/pathological regressions) + scripts/benchmark.py baseline reporter.

# TASK-0044 — Performance baselines + regression detection

Establish per-tool latency baselines using pytest-benchmark; wire CI to flag regressions >20% from baseline. Optional / quality-of-life — not strictly a blocker, but cheap to add once the test harness (TASK-0041) exists.

## Acceptance
- [ ] pytest-benchmark integrated into the test suite.
- [ ] Per-tool latency baseline captured for ≥10 representative inputs per tool.
- [ ] Baselines committed to repo as a JSON file; updated via explicit `pytest --benchmark-save` step.
- [ ] CI flags PRs with >20% regression vs baseline; comment on the PR with the diff.
- [ ] Performance budget documented per tool category: knowledge tools <50ms p95, capability tools <500ms p95, batch ops scale linearly with input.
