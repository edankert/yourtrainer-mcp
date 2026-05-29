---
type: "[[test]]"
id: TST-0010
title: "Docs-site generator suite"
status: passing
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: ["[[TASK-0055]]"]
scope: feature
kind: automated
level: unit
entrypoint: "pytest -q tests/test_docs_site.py"
requirements: []
features: ["[[FEAT-0001]]"]
issues: []
tasks: ["[[TASK-0055]]"]
artifacts: ["tests/test_docs_site.py", "src/yourtrainer_mcp/docs_site.py", "scripts/build_docs.py"]
evidence: ["142 passed (full suite); 10-page site generated"]
last_run: "2026-05-29"
related: []
---

# Docs-site generator suite

## Purpose
Verify the public docs-site mirror generator (TASK-0055) renders the knowledge
corpus to correct, safe static HTML.

## Expected results
- Builds an index plus one page per format (10 pages for the 9-format corpus).
- The index links every format; each page shows spec + examples + version.
- Examples are HTML-escaped (raw `<workout_file>` never emitted).
- Attribution footer present; no comparative content on any page.

## Evidence
- `142 passed in 1.95s`; ruff + mypy clean.
- `python scripts/build_docs.py` → "Wrote 10 pages to build/docs-site/".
