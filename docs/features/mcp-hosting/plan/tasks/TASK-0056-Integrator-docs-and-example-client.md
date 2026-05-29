---
type: "[[task]]"
id: TASK-0056
aliases: ["TASK-0056"]
title: "Integrator docs + example MCP client (workout creation + AI assistant flows)"
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

# TASK-0056 — Integrator docs + example MCP client

Publish the integrator-facing documentation (a PHASE-001 exit criterion) and a
runnable example client, so the upstream app integration (FEAT-0086) and the
workout-creation process have a clear contract to wire against.

## Acceptance
- [x] `docs/INTEGRATION.md`: how to connect (transports/config), the contract
  (stateless, file transfer, attribution), the tool catalogue by use-case, and
  worked flows for the in-app AI assistant and the workout-creation path.
- [x] `examples/client_demo.py`: runs the flows against an in-memory server.
- [x] Cross-linked from the README.

> **Done 2026-05-29 (CHG-20260529-11).** INTEGRATION.md + example client landed;
> demo verified end-to-end (build .ytw, decompose+scale ZWO, inspect a real ride
> NP 301.1 W). Live cross-link from the public docs site happens at deploy time.
