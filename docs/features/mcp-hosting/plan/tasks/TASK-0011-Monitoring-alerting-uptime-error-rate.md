---
type: "[[task]]"
id: TASK-0011
aliases: ["TASK-0011"]
title: "Monitoring + alerting (uptime + error-rate)"
status: doing
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-29
source: []
implements: ["[[FEAT-0002]]"]
fixes: []
effort: S
---

> **In progress 2026-05-29 (CHG-20260529-08).** deploy/healthcheck.sh + get_health + alerting guide; live alert channel pending the deployed host.

# TASK-0011 — Monitoring + alerting (uptime + error-rate)

External uptime monitor (UptimeRobot or Better Uptime) hitting `/health` every minute. Alert to Edwin's Discord or email on >5 min downtime. Server-side error-rate threshold alert if 5xx rate exceeds 1% over a 15-min window.

## Acceptance
- [ ] Uptime monitor configured and alerting in test (manually take server down → alert fires within SLA).
- [ ] Error-rate alert configured; tested with a deliberate 5xx induction.
- [ ] Alert destination documented (Edwin's Discord channel or email).
