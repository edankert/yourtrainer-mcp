---
type: "[[test]]"
id: TST-0014
title: "Activity tools: path | base64 alternation suite (TASK-0065)"
status: passing
owner: user:edwin
created: 2026-05-31
updated: 2026-05-31
source: ["[[TASK-0065]]"]
scope: feature
kind: automated
level: unit
entrypoint: "pytest -q tests/test_activity_input.py"
features: ["[[FEAT-0002]]"]
tasks: ["[[TASK-0065]]"]
artifacts: ["tests/test_activity_input.py", "src/yourtrainer_mcp/activity.py", "src/yourtrainer_mcp/server.py"]
evidence: ["213 passed (full suite); base64 inspect over the MCP client -> TSS 100"]
last_run: "2026-05-31"
related: ["[[ADR-0005]]"]
---

# Activity tools: path | base64 alternation

## Purpose
Verify single-activity tools accept inline base64 alongside path (hosted/mobile)
per TASK-0065 / the ADR-0005 addendum.

## Expected results
- `parse_activity_data(bytes, fmt)` parses fit/tcx/gpx; rejects non-activity fmt.
- `_activity_points`: path-only works; base64-only works; both -> error; neither
  -> error; malformed base64 -> error; oversize -> error; format mismatch
  (e.g. a ZWO) -> unsupported; `source_format` override honoured.
- Over the MCP protocol: `inspect_activity_file(document_base64=...)` yields a
  valid summary (1 h @ FTP -> TSS 100); both-args -> tool error; `detect_file`
  base64 detects `fit`.

## Evidence
- `213 passed`; ruff + mypy clean.
