# Contributing to yourtrainer-mcp

Thanks for your interest! This project is the MCP server + cycling-format
library behind [Your Trainer](https://www.your-applications.com/your-trainer/),
published under the MIT licence (see [ADR-0002](docs/decisions/ADR-0002-Open-Source-Publication.md)).

## Development setup

Requires Python 3.10+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"     # add ".[fit]" for FIT-binary support
pytest -q                    # run the suite
ruff check src tests scripts # lint
mypy src                     # type-check
```

All three (pytest, ruff, mypy) must be green; CI enforces them on Python 3.10
and 3.13.

## What we welcome

- **Format-corpus corrections** — fixes/additions to `src/yourtrainer_mcp/specs/*.json`
  (spec text, examples, constraints, conversion notes, glossary). Accuracy
  matters most here; cite a source where you can.
- **Capability fixes & hardening** — bugs in the power math, parsers, FIT codec,
  or workout tools. Include a test (a failing case that your change fixes).
- **New per-app constraints** for the acceptance checker — descriptive facts only.

## Ground rules

- **No comparative content, ever.** Per the project's positioning, nothing in
  the corpus, tool output, or docs claims any app is better/worse than another.
  Describe formats and constraints neutrally.
- **Statelessness is structural.** No per-user state, accounts, telemetry, or
  OAuth-mediated integrations — these are out of scope by design (see `CONTEXT.md`).
- **Determinism.** Capability tools must be pure and deterministic; add unit
  tests with known/reference values.
- **Keep the runtime lean.** Avoid new runtime dependencies; FIT support stays
  an optional extra.

## Documentation system

This repo uses the project-os docs system. For non-trivial changes, update
`SNAPSHOT.yaml` and the relevant note(s) under `docs/` in the same change
(see `tools/instructions/LIFECYCLE.md`). For a quick fix, a test + a one-line
`docs/changes/CHG-*` note is enough.

## Pull requests

- One focused change per PR; describe what and why.
- Green CI required. Add/adjust tests for behaviour changes.
- By contributing you agree your work is licensed under the project's MIT licence.
