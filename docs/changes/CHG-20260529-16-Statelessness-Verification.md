---
type: "[[change]]"
id: CHG-20260529-16
title: "Verify + enforce strict-statelessness (no rider data retained)"
status: merged
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: []
commit: ""
pr: ""
impacts: ["mcp-server", "privacy", "content"]
issues: []
features: ["[[FEAT-0002]]", "[[FEAT-0003]]"]
related: ["[[TASK-0064]]", "[[TST-0013]]", "[[RISK-0001]]"]
---

# Verify + enforce strict-statelessness

## Summary
Audited the codebase for any retention of rider/user content and made the
statelessness invariant enforceable.

**Audit result (clean):** no disk writes of user content (only the CLI docs-site
generator writes the public corpus to `build/`); no temp files; no logging/print
of anything; the only cross-call state is aggregate health counters (tool-name +
counts) and a cache of *public* website content (`content.py`, plus the packaged
public spec corpus in `registry.py`). Rider/activity/workout content is read,
processed in memory, and discarded.

**Enforced:**
- `tests/test_statelessness.py` (TST-0013): user content never enters the content
  cache; no working files written; health is aggregate-only; no cross-call bleed;
  the package emits no log records.
- `content.py` cache bounded + documented as public-content-only (defence in depth).
- `docs/PRIVACY.md`: the guarantee, why it is structural, and operator guidance
  (no request-body logging; non-persistent temp dirs — the systemd unit already
  sets PrivateTmp/ProtectSystem).

## Documentation Coverage (All Types Considered)
- features: not-applicable (verification)
- requirements: not-applicable
- tasks: new (TASK-0064, done)
- issues: not-applicable
- tests: new (TST-0013)
- workflows: not-applicable
- decisions: not-applicable
- risks: updated (RISK-0001 statelessness mitigation)
- changes: new (this note)
- snapshot: updated (TASK 63->64, metrics 60/64, TST-0013)

## Verification
- `pytest -q` -> 198 passed. ruff + mypy clean.
