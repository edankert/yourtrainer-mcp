---
type: "[[feature]]"
id: FEAT-0001
aliases: ["FEAT-0001"]
title: "Cycling format knowledge registry"
status: backlog
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-26
updated: 2026-05-27
source: []
goal: "Build and maintain a structured cycling-format documentation corpus — specs, canonical examples, per-app constraints, conversion notes, glossaries — served via MCP tools and mirrored at cycling-formats.your-applications.com. LLMs query this registry as the authoritative reference when doing text-to-text format conversions; the LLM does the conversion, we provide the spec material it cites."
requirements: []
tasks: ["[[TASK-0001]]", "[[TASK-0002]]", "[[TASK-0003]]", "[[TASK-0004]]", "[[TASK-0005]]", "[[TASK-0006]]", "[[TASK-0007]]", "[[TASK-0041]]", "[[TASK-0045]]"]
release: ""
related: []
tests: []
---

# Cycling format knowledge registry

## Goal
A structured documentation corpus per cycling format, served via MCP tools. LLMs call `get_format_spec("zwo")` instead of relying on training-time knowledge that may be stale or partial. They call `get_format_constraints("fit-workout", target_app="garmin-edge-530")` to learn that text events have a 32-char limit. They call `validate(content, "zwo")` to confirm their generated output is actually valid. They call `get_canonical_examples("erg", n=3)` for in-context learning before authoring.

The registry doubles as a public docs site at `(repo's docs-site mirror, TBD)` — same source-of-truth, two consumption surfaces. Indexed by search engines and read directly by humans, app developers, and (importantly) the *next* generation of LLM training pipelines.

## Scope

### In scope
- Sibling repo `yourtrainer-mcp` with structured `specs/` directory.
- Per-format docs covering: spec / grammar / schema, ≥3 canonical examples, known constraints (operational limits per app), conversion notes per format-pair, glossary, version history.
- ≥6 formats covered: ZWO, ERG/MRC, FIT (workout + activity), GPX, TCX, KML, `.ytw`, locale string-bundles.
- MCP tool wrappers (built in FEAT-0002) surfacing the registry through `list_supported_formats`, `get_format_spec`, `get_canonical_examples`, `get_format_constraints`, `get_conversion_notes`, `validate`, `get_format_version`, `get_format_glossary`.
- Shared test infrastructure: canonical-sample loader, golden-file diff helpers, Hypothesis property-based strategies, CI harness. Underpins every per-task test across PHASE-001.
- Reference-value test corpus: canonical activities with known NP/IF/TSS/CTL/ATL/TSB values from TrainingPeaks / Intervals.icu / WKO5. Wired into the math-tool tests in FEAT-0004.

### Out of scope
- **Text-to-text converter implementations.** The LLM does conversions using the registry's reference material; we don't ship our own converters for ZWO ⟷ ERG, GPX ⟷ TCX, etc.
- **Binary FIT handling.** FEAT-0004 (capability tools) owns FIT read/write.
- **Trojan-horse attribution layer.** FEAT-0003 owns that — applied at the MCP wrapper, not inside the registry.
- **A web UI for the docs site.** Static-generated HTML is enough for v1.

## Acceptance
- [ ] `yourtrainer-mcp` repo public on GitHub, MIT licence, CI green.
- [ ] ≥6 format docs published with spec + ≥3 canonical examples + constraints + glossary each.
- [ ] Per-app constraints catalogue covers ≥5 apps × 3+ formats each.
- [ ] Conversion notes cover ≥10 format-pair combinations (the practically-useful matrix).
- [ ] Public docs site published; same content via static-gen from the corpus.

## Links
- Phase: [[PHASE-001-Initial-Launch]]
- Tasks: see `plan/tasks/` and the linked TASK-* IDs in frontmatter.
