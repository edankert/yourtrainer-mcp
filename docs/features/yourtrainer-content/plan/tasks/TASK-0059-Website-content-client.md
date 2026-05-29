---
type: "[[task]]"
id: TASK-0059
aliases: ["TASK-0059"]
title: "Website content client (fetch + TTL cache + injectable fetcher)"
status: done
phase: "[[PHASE-001-Initial-Launch]]"
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: []
implements: ["[[FEAT-0007]]"]
fixes: []
effort: S
---

# TASK-0059 — Website content client (fetch + TTL cache + injectable fetcher)

`content.py`: stdlib urllib fetch of public website content, in-process TTL cache (public content only — statelessness-safe), injectable fetcher for hermetic tests, base-URL override. Per ADR-0006.

> **Done 2026-05-29 (CHG-20260529-14).**
