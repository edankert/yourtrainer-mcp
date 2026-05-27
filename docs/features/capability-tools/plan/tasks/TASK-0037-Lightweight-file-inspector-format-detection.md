---
type: "[[task]]"
id: TASK-0037
aliases: ["TASK-0037"]
title: "Lightweight file inspector + format detection"
status: backlog
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-27
source: []
implements: ["[[FEAT-0004]]"]
fixes: []
effort: S
---

# TASK-0037 — Lightweight file inspector + format detection

Two helper tools for the import path: `inspect_file(bytes_or_path) → {format, type, summary}` returns a quick *what-is-this* without the heavy NP/IF/TSS analysis. `detect_format(bytes) → {format, confidence}` identifies a file when extension is missing or wrong. Convenience tools that compose existing parsers; bundled for the common import-path UX flow.

## Acceptance
- [ ] `inspect_file` returns `{format, type: workout|activity|route, summary: short_string}` in under 100ms for canonical samples.
- [ ] `detect_format` returns the format name + confidence (0.0–1.0) from the first 4KB of bytes; supports all PHASE-001 formats.
- [ ] Both stateless.
