# Maintainers

yourtrainer-mcp is maintained by the team behind
[Your Trainer](https://www.your-applications.com/your-trainer/).

- **Lead maintainer:** Edwin Dankert (@edankert)

## Expectations

This is an open-source project published under MIT
([ADR-0002](docs/decisions/ADR-0002-Open-Source-Publication.md)). The hosted
instance at `mcp.your-applications.com/your-trainer` is the canonical service;
the repository is the reference implementation anyone may self-host.

To keep the maintenance burden sustainable (see
[RISK-0002](docs/risks/RISK-0002-OSS-Maintenance-Burden.md)):

- **Issues / PRs** are reviewed on a best-effort basis; this is not a commercial
  support channel. Clear, reproducible reports and focused PRs with tests get
  handled fastest.
- **In scope:** format-corpus accuracy, capability/parser/codec fixes,
  additional descriptive per-app constraints, performance, and docs.
- **Out of scope (by design):** stateful integrations (Strava/Garmin Connect
  OAuth, BLE push), per-user state/accounts/telemetry, and any comparative
  content about other apps. PRs adding these will be declined with a pointer to
  `CONTEXT.md`.
- **Security:** report suspected vulnerabilities privately to the lead
  maintainer rather than opening a public issue.

## Releasing

- Version lives in `pyproject.toml` / `src/yourtrainer_mcp/__init__.py`.
- A release is gated on green CI (pytest + ruff + mypy on 3.10 and 3.13) and the
  acceptance/verification gates in `tools/instructions/QUALITY.md`.
