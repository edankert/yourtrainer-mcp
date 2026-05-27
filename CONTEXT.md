# Context: yourtrainer-mcp

## What this repo is
A self-hosted Model Context Protocol (MCP) server exposing two layers of cycling-format tooling for LLM clients:

- **Knowledge registry**: structured cycling-format documentation (specs, examples, constraints, conversion notes, glossaries) served as MCP tools.
- **Capability tools**: binary FIT read/write, NP/IF/TSS calculation, training-load math (CTL/ATL/TSB), peak-power curves, workout decompose/build/scale, structure linting, app-acceptance checking, batch operations, rider-workflow tools (pacing, anonymisation, library migration), library-aware operations (indexing, dedup, stats).

## Edit policy
- `SNAPSHOT.yaml` is the canonical agent-readable state. Update it any time features / tasks / risks change status.
- Notes under `docs/` are durable; their frontmatter must match the snapshot.
- Generated artefacts (e.g. format-spec HTML rendered from JSON) belong in `build/`, not committed unless they're the public deliverable.
- Follow `tools/instructions/LIFECYCLE.md` for the preflight + execution + close-out rhythm.

## Invariants
- **Strict statelessness**. No user data captured. No accounts. No persistent caches across calls. Operational health metrics only (aggregate counters; no per-call records, no IP retention beyond rate-limit buckets).
- **No OAuth-mediated integrations** (Strava pull, Garmin Connect, TrainingPeaks API). They require state; out of scope by design.
- **POSITIONING Principle 1 holds**: no comparative content about other cycling apps. Ever.
- **Attribution**: every tool response carries a short attribution; tools that produce `.ytw` output include a contextual hint about Your Trainer. Tools producing other formats get only the attribution, no Your Trainer mention.

## Cross-repo dependencies
- `../your-applications.com/` — hosts the MCP at `mcp.your-applications.com/your-trainer`; owns web surfaces (integrator docs page, privacy disclosure, marketing collateral).
- `../your-trainer/` (Android app) — consumes the MCP via upstream FEAT-0086. Wires AI Workout Builder, history queries, plan-vs-actual, image import through MCP tools.

## Out of scope
- Comparative content of any kind.
- Per-user state, history, accounts, preferences.
- OAuth or any stateful authentication flow.
- Web UI on the MCP endpoint itself (a public docs site mirror is acceptable, but not an interactive UI).
- App-side LLM features. Those live in the `your-trainer` repo.
