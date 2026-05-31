---
type: "[[change]]"
id: CHG-20260531-19
title: "Align repo docs with the integrators page — complete the local-install story"
status: merged
owner: user:edwin
created: 2026-05-31
updated: 2026-05-31
source: ["external: your-applications.com/public/your-trainer/integrators.html"]
impacts: ["docs", "integration"]
issues: []
features: ["[[FEAT-0002]]", "[[FEAT-0003]]"]
related: ["[[ADR-0005]]"]
---

# Align repo docs with the integrators page (local install)

## Summary
The public integrators page defers local development / self-hosting / stdio to
"the source repository", but the repo only carried a dev-mode `pip install -e`
line + one client snippet. Filled that gap:

- `docs/INTEGRATION.md`: new **"Local install & self-hosting"** section — install
  via `pipx`/`pip` from git (+ `[fit]` extra), run stdio/HTTP, env vars, and
  **per-client registration for the LOCAL server** (Claude Desktop, Claude Code
  `claude mcp add`, Cursor, Codex `config.toml`, generic SDK) — the local mirror
  of the page's hosted-endpoint instructions.
- `README.md`: install section rewritten for integrators/self-hosters
  (`pipx install git+…`) rather than only the contributor `-e ".[dev]"` flow.
- Fixed a stale line in `INTEGRATION.md`: power is an **integer % of FTP**
  (`target_power_percent: 90`), not a fraction (the page's "fraction of FTP" line
  is the same staleness — flagged for a website update).

## Verification
- `pip install "git+https://github.com/edankert/yourtrainer-mcp"` in a clean venv:
  pip exit 0, `yourtrainer-mcp` entrypoint present, v0.1.0, 9 specs packaged,
  stdio boots.

## Findings flagged for the website (your-applications.com), not repo gaps
- Tool catalogue lists **31**; the repo serves **37** — the 6 FEAT-0007 Your
  Trainer content tools (`list_workout_library`, `get_library_workout`,
  `search_workout_library`, `list_ai_skills`, `search_manual`, `get_manual_section`)
  are missing from the page.
- The "File transfer contract" still says power is a **fraction** of FTP; the
  page's own sample uses integer % — internally inconsistent.
- **Conversion matrix overclaim:** the matrix implies the MCP converts ERG/MRC
  deterministically, but `build_workout_from_intent` emits only zwo/ytw/fit and
  `decompose_workout` reads only zwo/ytw. Per ADR/phase design, ERG/MRC are
  registry-documented and LLM-converted (grounded by `get_format_spec` /
  `get_conversion_notes`) — not a deterministic MCP tool. Resolve by either
  clarifying the page OR implementing deterministic ERG/MRC in build/decompose
  (see follow-up).

## Documentation Coverage
- features: not-applicable (docs)  · tasks: not-applicable (docs-only; CHG)
- decisions: ADR-0005 referenced  · changes: new (this note)
- snapshot: CHG seq bumped
