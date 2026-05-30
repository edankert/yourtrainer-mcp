---
type: "[[task]]"
aliases: ["TASK-0065"]
id: TASK-0065
title: "Activity-file tools accept base64 alongside path (mobile / hosted compatibility) — inspect_activity_file / analyze_ride / analyze_route / adherence_scorecard"
status: backlog
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-30
updated: 2026-05-30
source: ["external: ../your-trainer/docs/tasks/TASK-0613-WireHistoryQueriesToMcpMetrics.md", "[[TASK-0013]]"]
implements: ["[[FEAT-0002]]"]
fixes: []
effort: S
---

# TASK-0065 — Activity-file tools accept `document_base64` alongside `path`

## Context

Surfaced by the upstream `your-trainer/FEAT-0086` integration work
(TASK-0613, TASK-0615): the four single-activity-file capability tools
currently expose **path-only** signatures, which de-facto blocks them from
the hosted endpoint at `mcp.your-applications.com/your-trainer` — the
remote server cannot read a phone's filesystem. Per the existing ADR-0005
(file-transfer protocol):

> "Local files / libraries are referenced by **filesystem path**
> (`inspect_activity_file`, `analyze_ride`, `index_library`, `batch_inspect`).
> The host process reads them; the server stores nothing."
>
> "If a future hosted scenario needs remote files, that is a separate
> stateful service outside PHASE-001 scope."

The mobile/hosted scenario does not require a stateful service — base64
inlining as already used for FIT workouts (`read_fit_workout(document_base64)`,
`validate("fit", base64...)`) is sufficient. Path-only is the bug, not paths
themselves: the local-stdio / co-located-host story remains the right design
for bulk operations (`index_library`, `batch_inspect`, `library_statistics`).
Those tools stay path-only.

## Decision proposed

Add `document_base64?: string` to the four **single-activity-file** tools
alongside the existing `path?: string`. Server-side validate "exactly one
of {path, document_base64}" — same semantic split the FIT entry already
uses. Bulk-path tools (`index_library`, `batch_inspect`, `library_statistics`)
are **unchanged** — bulk-from-base64 would explode request size + tail-call
ergonomic value for the local stdio coach scenario.

| Tool                       | Path field                | New base64 field        |
|----------------------------|---------------------------|--------------------------|
| `inspect_activity_file`    | `path: str` → `path?`     | `document_base64?: str` |
| `analyze_ride`             | `path: str` → `path?`     | `document_base64?: str` |
| `analyze_route`            | `path: str` → `path?`     | `document_base64?: str` |
| `adherence_scorecard`      | `activity_path: str` → `activity_path?` | `activity_base64?: str` |

The workout half of `adherence_scorecard` (`workout_document` / `workout_format`)
is already inline-string and unchanged.

`document_base64` decodes to bytes; format is sniffed from a leading-bytes
heuristic (or required via an explicit `source_format?` if heuristic is unsafe
— defer the call to implementation).

## Acceptance

- [ ] Signatures expose both `path?` and `document_base64?` (resp.
      `activity_path?` and `activity_base64?` for `adherence_scorecard`).
- [ ] Server validates "exactly one of {path, base64}" and emits a clear
      `MCP tool '<name>' error: provide either 'path' or 'document_base64',
      not both` on violation.
- [ ] Base64 decode failure surfaces as a tool error with the format reason
      (no partial computation).
- [ ] Backwards compatible: existing path-only callers continue to work
      with no client changes required.
- [ ] Unit tests cover (a) path-only existing path, (b) base64-only new
      path, (c) both-provided rejection, (d) neither-provided rejection,
      (e) malformed base64 rejection, (f) format mismatch (e.g. a PDF
      sent as `document_base64` with FIT-sniffed bytes) yields a clean
      "unsupported format" error.
- [ ] ADR-0005 amended (see below) — either supersede with ADR-0007 or
      add an addendum section recording the alternation pattern.

## ADR-0005 amendment scope (small, doc-only)

The existing accepted ADR-0005 enumerates path-based tools as:

> `inspect_activity_file`, `analyze_ride`, `index_library`, `batch_inspect`.

Live signatures show two additional path-based tools that are not in that
list:

- `analyze_route(path, ftp_watts, target_intensity)` — single-route
  analysis.
- `adherence_scorecard(workout_document, workout_format, activity_path, ftp_watts)`
  — workout half is inline, activity half is path.

The amendment should:

1. List those two tools alongside the existing four under the path-based
   section.
2. Record the **"path | document_base64 — exactly one"** alternation pattern
   as the canonical shape for single-file activity tools that need to work
   from both local stdio and remote hosted clients.
3. Keep bulk path-only tools (`index_library`, `batch_inspect`,
   `library_statistics`) explicitly **scoped out** of the alternation — they
   stay path-only because bulk-from-base64 doesn't make sense.

The amendment does NOT change the ADR's spirit (statelessness, no stored
uploads, no URL handoff). It tightens the doc to match what the alternation
pattern was implicitly buying.

## Why this is small

The transport pattern is already proven (`read_fit_workout(document_base64)`
+ `validate("fit", base64)` use exactly the same shape). Each tool gains a
single new branch that delegates to the existing file-bytes processing
codepath after a `base64.b64decode(...)`.

## Why this matters upstream

Unblocks two rider-facing flows on `your-trainer` (the in-app client):

- **TASK-0613 (history queries)** — per-ride NP / IF / TSS / peak-power
  / decoupling / time-in-zone. Today the app side has landed the *partial*
  slice (`training_load(dated_tss)` for CTL/ATL/TSB — pure JSON, no
  transfer concern). The per-ride deep-dive waits on this task.
- **TASK-0615 (post-ride adherence scorecard)** — plan-vs-actual scorecard
  for each completed structured workout. Foundational for the upstream
  FEAT-0084 AI Coach analyst mode.

## Out of scope

- Bulk activity-from-base64 (`batch_inspect`, `index_library`,
  `library_statistics`). Stays path-only by design.
- URL handoff / pre-signed uploads / stateful storage. Still rejected per
  ADR-0005.
- Hosted-side caching of the inline bytes. Stateless contract preserved.
