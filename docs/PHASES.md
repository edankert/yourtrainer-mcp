# Phase Registry — yourtrainer-mcp

This document is the registry overview for the MCP project's phases. Phase notes live under `docs/phases/`.

## How Phases Work

- **Property**: `phase` (`[[PHASE-####]]` link preferred)
- **Location**: YAML frontmatter of features, tasks, requirements, risks
- **Purpose**: groups related work into delivery milestones

## Phase Definitions

| Phase | Name | Description | Key Deliverables |
|-------|------|-------------|------------------|
| [PHASE-001](phases/PHASE-001-Initial-Launch.md) | Initial Launch | Stand up the MCP server end-to-end: knowledge registry corpus, capability tools, MCP hosting, attribution policy, web-content coordination. Bundled launch with `your-applications.com/` FEAT-0025 (web surfaces) + `your-trainer/` FEAT-0086 (app integration). | Knowledge registry covering 8 cycling formats; FIT binary handler; NP/IF/TSS + CTL/ATL/TSB + HR decoupling + peak power curves; workout decompose/build/scale; pacing generator; library ops; self-hosted MCP at mcp.your-applications.com/your-trainer; integrator docs cross-published to the website. |

## Usage

Phase IDs in frontmatter:

```yaml
---
type: "[[task]]"
id: TASK-0001
phase: "[[PHASE-001-Initial-Launch]]"
status: backlog
parent: "[[FEAT-0001]]"
---
```
