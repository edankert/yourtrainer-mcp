---
type: "[[adr]]"
id: ADR-0005
title: "File transfer: paths for local files, base64 for binary in/out"
status: accepted
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: ["[[TASK-0013]]"]
decision: "Activity/library tools take filesystem paths; binary documents (FIT) cross the MCP boundary as base64 strings. No upload service, no URL handoff in v1."
context: "MCP tool args are JSON; binary files (FIT) and bulk activity files need a transfer convention compatible with strict statelessness."
alternatives: ["URL handoff / pre-signed uploads", "Multipart upload endpoint", "Always base64 everything"]
consequences: ["Stateless and simple; nothing is stored server-side.", "Large files are limited by request size; bulk ops take paths the host can read.", "Text formats pass as plain strings; only FIT uses base64."]
supersedes: ""
superseded: ""
related: ["[[TASK-0013]]", "[[FEAT-0002]]", "[[PHASE-001-Initial-Launch]]"]
---

# File transfer protocol

## Context
MCP tool arguments are JSON. Cycling work involves binary files (FIT) and
sometimes many files (library/batch ops). We need a transfer convention that
respects strict statelessness — no stored uploads, no retained data.

## Decision
- **Text documents** (ZWO, .ytw, GPX, TCX, ERG/MRC) pass as plain string args
  and are returned as strings.
- **Binary documents** (FIT) cross the boundary **base64-encoded**:
  `build_workout_from_intent(output_format="fit")` returns base64;
  `read_fit_workout` / `validate("fit", ...)` accept base64.
- **Local files / libraries** are referenced by **filesystem path**
  (`inspect_activity_file`, `analyze_ride`, `index_library`, `batch_inspect`).
  The host process reads them; the server stores nothing.
- **No upload service and no URL handoff in v1.**

## Alternatives
- **URL handoff / pre-signed uploads** — needs stateful storage + lifecycle;
  conflicts with statelessness.
- **Multipart upload endpoint** — same statefulness problem; also not idiomatic MCP.
- **Always base64** — wasteful for text; strings are clearer for text formats.

## Consequences
- Simple and stateless: files are processed in memory and discarded.
- Inline (base64/string) payloads are bounded by request size; very large
  activity sets are handled via path-based batch tools the host can read.
- If a future hosted scenario needs remote files, that is a separate stateful
  service outside PHASE-001 scope.
