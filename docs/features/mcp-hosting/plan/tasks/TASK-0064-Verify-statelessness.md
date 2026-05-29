---
type: "[[task]]"
id: TASK-0064
aliases: ["TASK-0064"]
title: "Verify + enforce strict-statelessness (no rider data retained)"
status: done
phase: "[[PHASE-001-Initial-Launch]]"
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: []
implements: ["[[FEAT-0002]]"]
fixes: []
effort: S
---

# TASK-0064 — Verify + enforce strict-statelessness

Audit the codebase for any retention of user/rider content and make the
statelessness invariant enforceable.

## Findings (audit)
- No disk writes of user content anywhere (only `docs_site.py` writes the public
  format corpus to `build/`, via a CLI — not a tool). No temp files.
- No logging/print of anything in the library.
- Only cross-call state: aggregate health counters (tool-name + counts) and a
  public-content cache (`content.py`); `registry.py` caches the packaged public
  spec corpus. None hold rider data.

## Done
- [x] `tests/test_statelessness.py` (TST-0013) enforces: user content never
  enters the content cache; no working files written; health is aggregate-only;
  no cross-call bleed; package emits no log records.
- [x] Hardened the content cache (bounded; documented public-content-only contract).
- [x] `docs/PRIVACY.md` documents the guarantee + operator guidance; RISK-0001 updated.

> **Done 2026-05-29 (CHG-20260529-16, [[TST-0013]]).**
