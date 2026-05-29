---
type: "[[test]]"
id: TST-0013
title: "Statelessness / privacy invariant suite (no rider data retained)"
status: passing
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: ["[[TASK-0064]]"]
scope: system
kind: automated
level: unit
entrypoint: "pytest -q tests/test_statelessness.py"
features: ["[[FEAT-0002]]", "[[FEAT-0003]]"]
tasks: ["[[TASK-0064]]", "[[TASK-0017]]"]
artifacts: ["tests/test_statelessness.py", "docs/PRIVACY.md"]
evidence: ["198 passed (full suite); 6 statelessness assertions"]
last_run: "2026-05-29"
related: ["[[RISK-0001]]"]
---

# Statelessness / privacy invariant suite

## Purpose
Enforce that the server retains no rider/user content (CONTEXT.md invariant).

## Expected results
- Processing a rider activity + authored workout + uploaded GPX leaves the
  public-content cache empty (user content never cached).
- The content cache only ever holds public site paths.
- Health metrics are aggregate-only (tool-name + integer counts; fixed key set).
- No working files are written during processing.
- Repeated calls are independent (no cross-call bleed).
- The package emits no log records (cannot leak content into logs).

## Evidence
- `198 passed`; ruff + mypy clean.
