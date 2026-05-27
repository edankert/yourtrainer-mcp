---
type: "[[task]]"
id: TASK-0001
aliases: ["TASK-0001"]
title: "Bootstrap yourtrainer-mcp repo (Python package + CI + MIT licence + knowledge-registry structure)"
status: backlog
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-27
source: []
implements: ["[[FEAT-0001]]"]
fixes: []
effort: M
---

# TASK-0001 — Bootstrap yourtrainer-mcp repo (Python package + CI + MIT licence + knowledge-registry structure)

Stand up the sibling `yourtrainer-mcp` repo with the structure that supports both the knowledge registry (FEAT-0001) and the capability layer (FEAT-0004). Repo layout: `specs/<format>/` per-format docs corpus, `lib/` capability code, `mcp/` MCP wrappers, `tests/`, `pyproject.toml` (hatchling), MIT licence, CI (pytest + ruff + mypy + spec-validation step).

## Acceptance
- [ ] Repo public on GitHub under MIT licence.
- [ ] Directory layout supports both `specs/` (knowledge corpus) and `lib/` (capability code).
- [ ] `pip install -e .` works locally.
- [ ] CI green on first push.
- [ ] README sets the framing: knowledge registry + capability tools; links to public docs site and integrator docs.
