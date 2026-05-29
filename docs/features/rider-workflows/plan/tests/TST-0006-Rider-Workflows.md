---
type: "[[test]]"
id: TST-0006
title: "Rider workflows suite (route/pacing/anonymise/adherence/migration/roundtrip)"
status: passing
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: ["[[TASK-0029]]"]
scope: feature
kind: automated
level: unit
entrypoint: "pytest -q tests/test_route.py tests/test_anonymize.py tests/test_workflows.py"
requirements: []
features: ["[[FEAT-0005]]"]
issues: []
tasks: ["[[TASK-0029]]", "[[TASK-0030]]", "[[TASK-0031]]", "[[TASK-0032]]", "[[TASK-0034]]", "[[TASK-0048]]"]
artifacts: ["tests/test_route.py", "tests/test_anonymize.py", "tests/test_workflows.py", "src/yourtrainer_mcp/route.py", "src/yourtrainer_mcp/anonymize.py", "src/yourtrainer_mcp/adherence.py", "src/yourtrainer_mcp/workflows.py"]
evidence: ["107 passed (full suite), Python 3.13.13"]
last_run: "2026-05-29"
related: []
---

# Rider workflows suite

## Purpose
Verify FEAT-0005: route profile/climb detection, gradient-aware pacing,
GPX anonymisation, plan-vs-actual adherence, migration inventory, and the
conversion roundtrip harness.

## Expected results
- Route profile computes distance + elevation gain; climb detection finds a
  sustained climb and ignores flats; pacing targets climbs harder than the
  flat base and caps at 1.15×FTP.
- Anonymisation removes start/end privacy-zone points, optionally strips HR,
  and re-emits valid GPX with no device metadata.
- Adherence: perfect match ⇒ 100% compliance; too-easy ride ⇒ low compliance
  and negative deviation; non-positive FTP rejected.
- Migration inventory flags only workout files not already in the target format.
- Roundtrip reports lossless for a ZWO→.ytw conversion and detects duration loss.

## Evidence
- `107 passed in 1.05s`; ruff + mypy clean.
