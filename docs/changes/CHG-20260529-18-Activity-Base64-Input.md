---
type: "[[change]]"
id: CHG-20260529-18
title: "Activity tools accept base64 alongside path (mobile/hosted) — TASK-0065"
status: merged
owner: user:edwin
created: 2026-05-31
updated: 2026-05-31
source: []
commit: ""
pr: ""
impacts: ["mcp-server", "capability-tools", "hosting"]
issues: []
features: ["[[FEAT-0002]]"]
related: ["[[TASK-0065]]", "[[TASK-0013]]", "[[ADR-0005]]", "[[TST-0014]]"]
---

# Activity tools accept base64 alongside path (TASK-0065)

## Summary
The single-activity tools were path-only, which blocked the hosted endpoint
(the server can't read a remote/mobile client's filesystem). Added the proven
`path | document_base64` alternation:

- **Tools updated:** `inspect_activity_file`, `analyze_ride`, `analyze_route`,
  `adherence_scorecard` (`activity_path` | `activity_base64`), and `detect_file`
  — each takes **exactly one of** path or base64, with an optional
  `source_format` override (format is otherwise sniffed from content).
- **Core:** `activity.parse_activity_data(bytes, fmt)` + `parse_fit_bytes`
  (FIT from a `BytesIO`/bytes, fitparse-or-builtin); shared
  `server._activity_points(path, document_base64, source_format)` with
  exactly-one validation, base64-decode error handling, and a `MAX_INLINE_BYTES`
  (12 MB) size bound.
- **Bulk tools unchanged** (path-only by design): `index_library`,
  `batch_inspect`, `library_statistics`.
- **Backwards-compatible:** existing path callers need no change.

ADR-0005 amended with the alternation addendum (lists the two previously-missing
tools and records the canonical shape; statelessness spirit unchanged).

## Why
Unblocks upstream `your-trainer` FEAT-0086 flows: TASK-0613 (per-ride
NP/IF/TSS/peak-power/decoupling) and TASK-0615 (post-ride adherence) can now be
called from the app against the hosted endpoint.

## Documentation Coverage (All Types Considered)
- features: updated (FEAT-0002)
- tasks: updated (TASK-0065 → done)
- issues: not-applicable
- tests: new (TST-0014; tests/test_activity_input.py — full acceptance matrix)
- decisions: ADR-0005 amended (addendum)
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (TASK 64→65, metrics 62/65, TST-0014)

## Verification
- `pytest -q` → 213 passed. ruff + mypy clean.
- Over the MCP client: `inspect_activity_file(document_base64=…)` → TSS 100 on a
  1 h @ FTP fixture; both-args → tool error; `detect_file` base64 → `fit`.

## Follow-up
- Redeploy to the live box and confirm a base64 activity call works end-to-end.
