---
type: "[[risk]]"
id: RISK-0002
title: "Open-source maintenance burden (yourtrainer-mcp)"
status: open
owner: edwin
created: 2026-05-27
updated: 2026-05-27
source: []
likelihood: medium
impact: medium
mitigation:
  - "Clear MAINTAINERS.md sets response-time expectations (best-effort, no SLA)."
  - "Strong CI catches contributor mistakes before review."
  - "Issue templates + contributor guidelines reduce noise."
  - "Triage cadence: weekly 30-min sweep, no commitment to fix or merge."
  - "Stalebot for issues with no maintainer/reporter action in 90 days."
related:
  - "[[FEAT-0001-Cycling-Format-Library]]"
  - "[[FEAT-0003-Cycling-Format-Trojan-Horse]]"
  - "[[PHASE-001-Initial-Launch]]"
---

# Open-source maintenance burden

## Description
If TASK-0018's ADR results in publishing `yourtrainer-mcp` as OSS (the phase recommendation), expect:
- Bug reports — many of which will be "the converter produced output my-favourite-app didn't accept" without the canonical test file Edwin can reproduce against.
- Feature requests — every cycling app's workout format becomes a candidate (TrainerRoad cloud-export, MyWhoosh cloud-export, ROUVY format). Most aren't viable because the source format is behind a login wall.
- PRs — code contributions need review, CI runs, mergeable in a timely window or contributors lose interest.
- Support questions — install issues, integration questions, "does this work with X?" enquiries.

For a one-person team this can become a non-trivial time sink. Trojan-horse strategy depends on the project being *seen as alive*; abandoning it after a year erodes the brand association.

## Mitigation
- **Set expectations upfront in MAINTAINERS.md.** *"Maintained best-effort by the team behind Your Trainer. Response times are not guaranteed. Pull requests welcome but may sit unreviewed during active Your Trainer development cycles."* Saying it explicitly stops the implicit-SLA problem before it starts.
- **Issue templates.** Bug report needs: canonical sample file (must be attachable to the issue), expected vs actual, environment. No template → close with template prompt.
- **Contributor guidelines.** PRs need: tests for the change, CI green, no dependency additions without discussion. Reduces "wide-net PR" noise.
- **Strong CI.** Catches lint, type, and test failures before Edwin sees the PR. Free filter on contributor quality.
- **Triage cadence.** 30 min/week sweep of open issues + PRs. Either action or label-and-defer. No long-form responses unless the report is exceptional.
- **Stalebot.** Auto-close issues / PRs with 90 days of no reporter / contributor action. Reduces graveyard buildup.
- **Maintainer-of-last-resort framing.** Make clear that the Your Trainer team is one of several possible maintainers, not the sole owner. Invites others to take responsibility for sub-areas (e.g. one contributor owns the FIT format; another owns ZWO; etc.).

## Notes
The 90-day re-evaluation post-launch is the right window. If maintenance is materially cutting into Your Trainer development, options are: increase triage cadence to monthly, archive the repo (keep code public but signal not-active), or transition to a maintainer outside the Your Trainer team. None of these break the trojan-horse benefit retroactively.
