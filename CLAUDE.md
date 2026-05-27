# Project: yourtrainer-mcp

Read `SNAPSHOT.yaml` at session start to understand current project state and focus.
Read `CONTEXT.md` for the full edit policy and invariants.

This repo is the **MCP server + cycling format-tools library** maintained by the team behind [Your Trainer](https://www.your-applications.com/your-trainer/). Hosted at `mcp.your-applications.com/your-trainer`. MIT-licensed (publication date governed by the OSS ADR).

## project-os documentation system (core rules — always active)

@tools/instructions/LIFECYCLE.md

## Reference instructions (read when relevant)

- Status values and transitions: tools/instructions/STATUSES.md
- Quality gates and close-out checks: tools/instructions/QUALITY.md
- Snapshot structure and update rules: tools/instructions/SNAPSHOT.md
- Allowed taxonomy values: tools/instructions/TAXONOMY.md
- Required link graphs: tools/instructions/TRACEABILITY.md
- ADR conventions: tools/instructions/DECISIONS.md
- Ownership rules: tools/instructions/OWNERSHIP.md
- Obsidian conventions: tools/instructions/OBSIDIAN.md
- Handoff/recovery: tools/instructions/HANDOFF.md
- Hook contracts: tools/instructions/HOOKS.md
- Testing conventions: tools/instructions/TESTING.md
- Product positioning (governs any rider-facing copy in tool responses + docs): `../your-trainer/docs/marketing/POSITIONING.md`

## Project-specific notes

- **What this ships**: a stateless MCP server exposing cycling-format knowledge + capability tools (FIT binary handling, NP/IF/TSS, training-load math, workout build/decompose/scale, format validators, pacing strategy, activity privacy, library operations).
- **Hosted endpoint**: `mcp.your-applications.com/your-trainer` (self-hosted on Edwin's VPS).
- **Sibling repos**:
  - `../your-applications.com/` — web surfaces (integrator docs page, privacy disclosure, marketing copy). The website hosts the MCP at the URL above; this repo provides the deploy artefact.
  - `../your-trainer/` — Android app. Wires through to this MCP via upstream FEAT-0086 (MCP integration for in-app AI features).
- **Strict statelessness**: no rider data captured, no usage telemetry, no OAuth-mediated integrations. See PHASE-001 phase note.
- **POSITIONING constraint**: no comparative content with other cycling apps; brand attribution surfaces only where contextually relevant. Tools mention Your Trainer the same way an open-source project mentions its sponsor.
