---
type: "[[test]]"
id: TST-0008
title: "MCP conformance + health-metrics suite"
status: passing
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: ["[[TASK-0042]]"]
scope: feature
kind: automated
level: integration
entrypoint: "pytest -q tests/test_conformance.py tests/test_health.py"
requirements: []
features: ["[[FEAT-0002]]", "[[FEAT-0003]]"]
issues: []
tasks: ["[[TASK-0042]]", "[[TASK-0017]]"]
artifacts: ["tests/test_conformance.py", "tests/test_health.py", "src/yourtrainer_mcp/health.py", "src/yourtrainer_mcp/server.py"]
evidence: ["118 passed; 31 tools listed over the in-memory MCP client"]
last_run: "2026-05-29"
related: ["[[ADR-0001]]"]
---

# MCP conformance + health-metrics suite

## Purpose
Drive the real MCP request path (initialize / list_tools / call_tool) via the
in-memory FastMCP client (TASK-0042), and verify the aggregate-only health
metrics (TASK-0017).

## Expected results
- The server lists the full tool surface (31 tools) over the protocol.
- `call_tool` round-trips build/validate and returns structured `.data`.
- Every tool result carries the `_attribution` block (FEAT-0003).
- Health counters are aggregate-only — request/error totals, per-tool counts,
  uptime — with no per-call records or rider data.

## Evidence
- `118 passed in 0.97s`; ruff + mypy clean.
- In-memory client lists 31 tools; build/validate/health calls verified.
