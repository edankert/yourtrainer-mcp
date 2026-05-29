---
type: "[[task]]"
id: TASK-0001
aliases: ["TASK-0001"]
title: "Bootstrap yourtrainer-mcp repo (Python package + CI + MIT licence + knowledge-registry structure)"
status: done
phase: "[[PHASE-001-Initial-Launch]]"
owner: user:edwin
created: 2026-05-27
updated: 2026-05-29
source: []
implements: ["[[FEAT-0001]]"]
fixes: []
effort: M
---

> **Closed 2026-05-29 (CHG-20260529-01).** Package scaffolded: `pyproject.toml`
> (hatchling, `src/` layout), MIT `LICENSE`, `.github/workflows/ci.yml`
> (ruff + mypy + pytest on 3.10/3.13), `src/yourtrainer_mcp/` with lib + MCP
> wrapper. `pip install -e .` verified; suite green. Per ADR-0001 the layout is
> `src/yourtrainer_mcp/{power,activity,formats,attribution,server}.py` +
> `tests/`; the `specs/` knowledge corpus lands in TASK-0002..0007.

# TASK-0001 — Bootstrap yourtrainer-mcp repo (Python package + CI + MIT licence + knowledge-registry structure)

Stand up the sibling `yourtrainer-mcp` repo with the structure that supports both the knowledge registry (FEAT-0001) and the capability layer (FEAT-0004). Repo layout: `specs/<format>/` per-format docs corpus, `lib/` capability code, `mcp/` MCP wrappers, `tests/`, `pyproject.toml` (hatchling), MIT licence, CI (pytest + ruff + mypy + spec-validation step).

## Acceptance
- [ ] Repo public on GitHub under MIT licence.
- [ ] Directory layout supports both `specs/` (knowledge corpus) and `lib/` (capability code).
- [ ] `pip install -e .` works locally.
- [ ] CI green on first push.
- [ ] README sets the framing: knowledge registry + capability tools; links to public docs site and integrator docs.
