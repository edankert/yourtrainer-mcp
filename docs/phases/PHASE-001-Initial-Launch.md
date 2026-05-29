---
type: "[[phase]]"
id: PHASE-001
aliases: ["PHASE-001"]
title: "Initial Launch (knowledge registry + capability tools + hosting)"
status: active
order: 1
owner: user:edwin
created: 2026-05-26
updated: 2026-05-29
goal: "Publish a self-hosted MCP server at mcp.your-applications.com exposing two layers for the broader indoor-cycling ecosystem: a knowledge registry (cycling-format specs, examples, constraints, conversion notes, glossaries — the authoritative reference material LLMs cite) and a narrow capability layer (binary FIT read/write, NP/IF/TSS calculations, workout linting, batch ops — the genuinely tool-required operations LLMs can't do alone). Trojan-horse adoption pattern: become the citation source for cycling-format knowledge."
features:
  - "[[FEAT-0001-Cycling-Format-Knowledge-Registry]]"
  - "[[FEAT-0002-Cycling-Format-MCP-Hosting]]"
  - "[[FEAT-0003-Cycling-Format-Trojan-Horse]]"
  - "[[FEAT-0004-Cycling-Capability-Tools]]"
  - "[[FEAT-0005-Cycling-Rider-Workflows]]"
  - "[[FEAT-0006-Cycling-Library-Operations]]"
requirements: []
tasks: []
issues: []
depends_on: []
related:
  - "[[FEAT-0017-MCP-Server]]"
tags: ["llm", "ai", "mcp", "format-registry", "ecosystem", "trojan-horse"]
---

# Phase 5: Initial Launch (knowledge registry + capability tools + hosting)

## Goal
The first draft of this phase scoped a converter library — bidirectional text-format converters for ZWO, ERG/MRC, GPX, TCX, etc. A sharper review concluded that LLMs already do text-to-text format conversion natively. What they *can't* do is:

1. Cite an authoritative, always-current reference for those formats (training data goes stale; user-prompts re-author the same specs per task).
2. Process binary formats (FIT, proprietary binary blobs).
3. Compute time-series metrics (NP, IF, TSS, peak-power curves).
4. Mediate real protocols (Strava OAuth, BLE to bike computers).
5. Enforce institutional knowledge (per-app constraints like *"Garmin Edge 530 crashes on FIT-workouts with text events > 32 chars"*).

This phase therefore ships **two MCP layers** that together cover those gaps:

- A **knowledge registry** (FEAT-0001) — structured cycling-format documentation served via MCP tools. Specs, canonical examples, per-app constraints, conversion gotchas, glossaries. The LLM does conversions; we provide the reference material. Also doubles as a public docs site indexed for direct human reading and future LLM training data.
- A **capability tools layer** (FEAT-0004) — the narrow set of tools the LLM genuinely can't do alone. Binary FIT handlers, NP/IF/TSS calculators, workout structure linters, batch operations.

Both layers ship through the same self-hosted MCP server (FEAT-0002) at `mcp.your-applications.com/your-trainer`. A trojan-horse adoption layer (FEAT-0003) handles attribution and the citation-source framing: every spec read carries an attribution, every contextual hint surfaces Your Trainer where format-relevant, no comparative content ever.

POSITIONING Principle 1 holds throughout — at no point does any tool claim Your Trainer is better than any other app. Tools mention Your Trainer the same way an open-source project mentions its sponsor.

## Design principle: strict statelessness

The MCP server is **stateless**. No user data is captured or retained:

- No accounts, profiles, or rider identity tracked.
- No per-user file uploads stored beyond the duration of a single tool call. Files are processed in memory and discarded.
- No usage analytics or behavioural telemetry. Operational health metrics (aggregate request count, error count, latency) are aggregate-only — no per-call record, no IP retention beyond rate-limit buckets.
- No persistent caches that could leak data across calls.

This has two consequences worth being explicit about:

**(a) Privacy is structural, not policy.** The server architecturally cannot return rider X's data to rider Y because it never knows there is a *"rider X."* Reviewers and integrators can verify this from the code; users don't have to trust a privacy policy.

**(b) OAuth-mediated protocol integrations are out of scope.** Strava pull, Garmin Connect, TrainingPeaks API all require state — access tokens to hold, refresh tokens to rotate, callback URLs to receive responses. None of that fits a stateless MCP without architectural compromises. The user-facing flow for *"use my Strava data with the MCP"* is therefore: the rider exports their activity file from Strava (Strava offers this) and uploads the file to the MCP tool. Slower iteration but architecturally clean — the rider keeps custody of their data; we keep nothing.

This trades convenience for principle. Riders who want one-click Strava integration are not the target audience.

## Why a dedicated phase
Four concerns benefit from coherent acceptance:
1. **Knowledge registry** — structured format documentation maintained at a high signal-to-noise ratio. Different work from running code; needs domain depth.
2. **MCP hosting** — VPS provisioning, TLS, monitoring. Infrastructure, not content.
3. **Capability tools** — the narrow set of binary/math/protocol tools. Real code, real tests.
4. **Trojan-horse adoption** — attribution, citation framing, telemetry, integrator docs.

The knowledge layer is the larger and more novel piece — most of the trojan-horse leverage comes from being *"the authoritative cycling-format documentation source the LLM cites"* rather than *"a place that converts files."*

This phase is **independent of PHASE-004**. Both result in MCP servers, but they serve different audiences with different data: PHASE-004's MCP serves agents asking about Your Trainer specifically; PHASE-001's serves the broader indoor-cycling ecosystem. They share infrastructure decisions (transport, framework, hosting platform) — recommendation is to align TASK-0065 and TASK-0008 ADRs on the same runtime + framework so the hosting story is uniform.

## Scope

### In scope

**Knowledge layer (FEAT-0001)**
- Structured documentation corpus per cycling format: ZWO, ERG/MRC, FIT (workout + activity), GPX, TCX, KML, `.ytw`, locale string-bundles.
- Per-format docs include: spec / grammar / schema, canonical examples (≥3 per format), known constraints (per-app limits), conversion notes per format-pair, glossary, version history.
- MCP tools that surface this corpus: `list_supported_formats`, `get_format_spec`, `get_canonical_examples`, `get_format_constraints`, `get_conversion_notes`, `validate`, `get_format_version`, `get_format_glossary`.
- Public docs site mirror at `(repo's docs-site mirror, TBD)` — same source-of-truth, two consumption surfaces.

**Capability layer (FEAT-0004)**
- Binary FIT read/write (workout and activity formats; Garmin SDK-backed).
- Activity-file inspector → JSON summary (duration, distance, peak power, NP, IF, TSS, time-in-zone, elevation gain).
- Peak power curve calculator (mean-max 1s, 5s, 30s, 1min, 5min, 20min, 60min).
- Workout builder from structured intent (`{warmup, intervals, cooldown}` → ZWO + FIT + `.ytw` deterministically).
- App-acceptance checker (given a workout, returns which apps will load it cleanly per the constraints catalogue).
- Workout structure linter (domain-aware static analysis against canonical patterns).
- Batch operations adapter (folder-of-files → aggregated results).
- **Training-load curve (CTL / ATL / TSB)** from a folder of activities — exponentially-weighted moving averages of TSS for fitness / fatigue / form analysis.
- **HR–power decoupling** for endurance rides — pace-quality metric.
- **Workout decomposition** (file → structured intent) — symmetric inverse of the builder; closes the read-back gap so agents can modify existing workouts without re-authoring from scratch.
- **Workout scaling** (duration / FTP / intensity) — deterministic rules for the common *"give me a 30-min version of this"* request.
- **Lap / interval auto-detection** on unstructured activities — retrofit interval analysis to free-rides.
- **Lightweight file inspector + format detection** — *what-is-this* helpers for the import path.

**Rider workflows (FEAT-0005)**
- Pacing strategy generator: GPX route + rider FTP + target effort → per-segment power/HR/cadence targets accounting for elevation gradient.
- Activity privacy / anonymisation: strip personal data from FIT/GPX files (start coordinates fuzzed within geofence, device IDs removed, HR stream optional).
- Library migration helper: LLM-orchestrated batch conversion across cycling-app libraries (e.g. TrainerRoad ERG/MRC → Zwift ZWO).
- Format-conversion roundtrip test harness: LLM converts X→Y; tool re-converts Y→X; compares to original; reports loss. Lets agents self-correct.
- Plan-vs-actual adherence scorecard: workout file + activity file + FTP → per-interval scorecard. Closes the planning-execution loop; pairs with upstream FEAT-0084 AI Coach as Training Partner.

**Library-aware operations (FEAT-0006)**
- Library indexing — searchable metadata index from a folder.
- Library deduplication — find near-identical workouts after migration.
- Library statistics — aggregate breakdown of *what's in this library*.

**Hosting (FEAT-0002)**
- Self-hosted MCP server on Edwin's VPS at `mcp.your-applications.com/your-trainer`.
- Both knowledge and capability tools served through the same endpoint.

**Trojan-horse layer (FEAT-0003)**
- Citation-source attribution: tool responses carry *"spec maintained at cycling-formats.your-applications.com by the team behind Your Trainer."*
- Contextual hints: when a tool produces or references `.ytw`, the response notes *"this format imports directly into Your Trainer."*
- Opt-in usage telemetry (anonymous), to size adoption.
- Open-source decision (TASK-0018 ADR) for the registry + tools.

### Out of scope
- **Text-to-text converter implementations** (ZWO ↔ ERG, ZWO ↔ `.ytw`, GPX ↔ TCX, locale-bundle conversion). LLMs do these natively, anchored against the FEAT-0001 knowledge registry. Shipping our own converter implementations would duplicate work the LLM does fine.
- **Real protocol integrations** (Strava OAuth pull, BLE direct push to cycling computers, TrainingPeaks API). These all require state (tokens, refresh, callbacks); incompatible with the strict-statelessness principle above. The rider-exports-then-uploads flow is the supported alternative. If protocol integrations are ever wanted, they need a separate stateful service which is not in PHASE-001 scope.
- **Cloud-only formats** behind login walls (TrainerRoad cloud library, MyWhoosh cloud, SYSTM cloud). We can document their *export* formats where they offer one; we don't scrape, screen-grab, or reverse-engineer their cloud APIs.
- **Comparative content of any kind.** POSITIONING Principle 1 stands.
- **Per-rider account state.** Stateless MCP.
- **A web UI on `mcp.your-applications.com`.** The public docs site (`cycling-formats.your-applications.com`) is human-readable already; an interactive UI is a follow-up.

## Exit Criteria
- [ ] Sibling `yourtrainer-mcp` repo published with MIT licence, knowledge registry for ≥6 formats, CI green.
- [ ] Knowledge layer: ≥6 format docs (ZWO, ERG/MRC, FIT, GPX/TCX/KML, `.ytw`, locale-bundles) with spec + ≥3 examples + constraints + glossary each.
- [ ] Capability layer: FIT-binary read/write working; NP/IF/TSS calculation validated against TrainingPeaks reference values for canonical samples; workout-builder produces ZWO + FIT + `.ytw` from structured intent.
- [ ] MCP server deployed at `mcp.your-applications.com/your-trainer` with both layers exposed; ≥99% uptime over 30 days.
- [ ] Public docs site at `(repo's docs-site mirror, TBD)` mirrors the registry content.
- [ ] Attribution + citation-hint copy reviewed against POSITIONING.md (no comparative phrasing) and applied consistently.
- [ ] Integrator docs published; cross-linked from the docs site, GitHub README, `your-applications.com/integrators.html`.

## Dependencies
- **Internal:** None hard. Shares MCP-framework decision-space with PHASE-004's FEAT-0017.
- **External:** Format specs (FIT SDK, GPX schema, Zwift ZWO conventions). Library tracks their evolution.

## Risks
- **RISK-0001** — VPS uptime + security exposure (unchanged).
- **RISK-0002** — Open-source maintenance burden (unchanged; reframed since docs maintenance ≠ code maintenance — see risk note).
- **RISK-0003** — Format-spec drift (unchanged; now also covers the docs going stale, not just converters).

## Open-source recommendation (decided in TASK-0018 ADR)
- **Open-source the knowledge registry corpus and the capability library under MIT.** Pure win for a docs-heavy project: lowers adoption friction, invites domain contributors, and the trojan-horse benefits *more* from OSS because attribution-in-the-docs is the strategy.
- **Keep the hosted MCP instance at `mcp.your-applications.com/your-trainer` as the canonical service.** Plausible / Mastodon model.

## Coordinated landing — bundled with curated library + app integration

PHASE-001 ships **as one launch moment** alongside two related pieces:

- **FEAT-0009** (Your Trainer curated workout library, in PHASE-003) — the 10–20 starter `.ytw` files for riders who want a library without the AI builder. Curated using PHASE-001's own tools (`build_workout_from_intent`, `lint`, workout difficulty score, app-acceptance checker) so each file has provenance.
- **Upstream FEAT-0086** (Your Trainer app's MCP wiring) — the in-app integration that makes the MCP useful to riders via Claude / OpenAI / Gemini, including image-import (TASK-0618) for *"bring your TrainerRoad / Zwift / Wahoo workout to Your Trainer via screenshot."*

Why bundle:
1. **Marketing leverage**: one launch with three value-adds is materially stronger than three separate launches. The "TR alternative" pitch specifically benefits — riders see *"bring your existing library + use our starter set + the in-app AI is now actually good"* simultaneously.
2. **Internal dog-fooding**: PHASE-001 capability tools are used during library curation (FEAT-0009 TASK-0018). The same tools we publish are the ones we author with. Strongest possible signal that the tools work.
3. **Honest framing**: FEAT-0009 alone is modest (a small curated set). PHASE-001 alone is infrastructure (no UX). Bundled, they cover the rider's full *"how do I get a workout into Your Trainer?"* path: AI build, bring from another app via image, use the curated set, or convert any format. Four routes, one moment.

Sequencing implications:
- PHASE-001 capability tools (TASK-0023 `build_workout_from_intent`, TASK-0025 `lint`, TASK-0024 `app_acceptance_check`, TASK-0050 workout difficulty score) need to ship **before** FEAT-0009 TASK-0018 begins curation — those tools are how curation gets done.
- FEAT-0009 TASK-0019 (download UX on `workouts.html`) is independent and can land in parallel.
- Upstream FEAT-0086 work can start in parallel to PHASE-001 once its dependency tasks ship (notably TASK-0012 MCP wrappers, TASK-0023 build, TASK-0021 inspector).
- The launch moment requires all three to be production-ready: MCP server live, library files curated and downloadable, app build with MCP wiring shipped to Play Store.

## Notes
The knowledge registry doubles as internal infrastructure: the locale string-bundle docs support the website's translation pipeline. The capability tools' workout-builder can drop into the AI Coach prompt context to improve workout-generation quality. Multiple "we eat our own dog food" angles emerge naturally.
