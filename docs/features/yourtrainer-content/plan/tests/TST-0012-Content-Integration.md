---
type: "[[test]]"
id: TST-0012
title: "Your Trainer content integration suite (library/skills/manual)"
status: passing
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: ["[[TASK-0059]]"]
scope: feature
kind: automated
level: unit
entrypoint: "pytest -q tests/test_content.py"
features: ["[[FEAT-0007]]"]
tasks: ["[[TASK-0059]]", "[[TASK-0060]]", "[[TASK-0061]]", "[[TASK-0062]]"]
artifacts: ["tests/test_content.py", "src/yourtrainer_mcp/content.py", "tests/fixtures/website/"]
evidence: ["191 passed; live website fetch returns 26 workouts"]
last_run: "2026-05-29"
related: ["[[ADR-0006]]"]
---

# Your Trainer content integration suite

## Purpose
Verify the website content client + tools (workout library, AI skills, manual)
against local fixtures (hermetic, injected fetcher).

## Expected results
- Library: list (26 workouts), filter by set/duration, get-with-.ytw-body,
  search; metadata-only on list.
- Caching: a repeated manifest read fetches once.
- Manual: sections parsed from HTML; search returns snippets; get-section roundtrips.
- AI skills: catalogue parsed; "On this page" nav excluded.

## Evidence
- `191 passed`; ruff + mypy clean.
- Live smoke: real website manifest returns 26 workouts.
