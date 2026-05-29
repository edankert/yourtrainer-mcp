---
type: "[[feature]]"
id: FEAT-0007
title: "Your Trainer content integration (workout library + AI skills + manual)"
status: done
phase: "[[PHASE-001-Initial-Launch]]"
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
tags: ["mcp", "content", "trojan-horse"]
---

# FEAT-0007 — Your Trainer content integration

Make the MCP a **stateless proxy over public Your Trainer website content** so
LLM clients (and the in-app assistant) can pull the curated workout library, the
AI-assistant skill catalogue, and the product manual directly through the MCP.

## Scope
- `content.py` client: stdlib `urllib` fetch + TTL cache + injectable fetcher (ADR-0006).
- Workout-library tools: `list_workout_library`, `get_library_workout`, `search_workout_library`
  (manifest-driven, returns `.ytw` bodies on demand).
- AI-skill catalogue: `list_ai_skills` (parsed from ai-skills.html).
- Manual Q&A: `search_manual`, `get_manual_section` (parsed from manual.html).
- Restrained "Powered by Your Trainer" attribution + server instructions (TASK-0058).

## Invariants honoured
- Statelessness: caches **public content only**, never rider data.
- POSITIONING: attribution restrained, never comparative.

## Known follow-ups
- [[ISS-0001]] — our `.ytw` writer schema != the real Your Trainer `.ytw`.
- Website JSON endpoints for skills/manual would be more robust than HTML parsing.
- [[RISK-0004]] — website runtime dependency.
