---
type: "[[task]]"
id: TASK-0041
aliases: ["TASK-0041"]
title: "Test infrastructure — fixtures, golden files, Hypothesis strategies, CI harness"
status: done
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-29
source: []
implements: ["[[FEAT-0001]]"]
fixes: []
effort: M
---

> **Done 2026-05-29 (CHG-20260529-08).** Hypothesis property tests (roundtrip/FTP-independence/scale/FIT) + golden files + perf budgets; conftest fixtures + CI harness already in place.

# TASK-0041 — Test infrastructure — fixtures, golden files, Hypothesis strategies, CI harness

Shared test harness everything else builds on. Without it, every per-task test (FIT round-trips, NP/IF/TSS validation, format-spec validation, etc.) reinvents the same fixture-loading + golden-file-diff plumbing. Centralise it as one piece of infrastructure: canonical-sample loader, golden-file diff helpers, Hypothesis property-based-testing strategies for each format, deterministic-output assertions, CI harness wiring.

Layer 1 of the six-layer testing strategy. Foundational dependency for TASK-0002 onward (per-format docs) and all FEAT-0004 / FEAT-0005 / FEAT-0006 task tests.

## Acceptance
- [ ] `tests/` directory in `yourtrainer-mcp` with documented structure: `fixtures/<format>/<category>/`, `golden/<tool>/<scenario>.json`, `strategies/<format>.py`.
- [ ] Fixture loader: `load_sample(format, category, name)` returns parsed canonical samples.
- [ ] Golden-file helper: `assert_matches_golden(output, golden_path)` with auto-update mode behind a flag.
- [ ] Hypothesis strategies for ZWO, ERG/MRC, FIT-workout, GPX, TCX, KML, `.ytw` — generate valid random instances for property-based tests.
- [ ] Round-trip property test pattern documented: `parse(emit(parse(X))) == parse(X)` template usable across all formats.
- [ ] CI harness wires pytest + pytest-cov + pytest-benchmark + Hypothesis on every PR.
- [ ] Documented in `tests/README.md` so subsequent task authors know what to use.
