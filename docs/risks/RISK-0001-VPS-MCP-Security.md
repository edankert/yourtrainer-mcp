---
type: "[[risk]]"
id: RISK-0001
title: "VPS-hosted MCP server security + uptime exposure"
status: open
owner: edwin
created: 2026-05-27
updated: 2026-05-27
source: []
likelihood: low
impact: high
mitigation:
  - "Minimal attack surface — only Caddy/nginx + the MCP server exposed publicly; all other VPS services behind firewall / SSH-only."
  - "Run MCP server as a dedicated non-root user with no shell."
  - "fail2ban on SSH; unattended upgrades enabled for security patches."
  - "Container or systemd-confined sandbox if framework supports it."
  - "Health endpoint + uptime monitoring (TASK-0011)."
  - "Optional: sign converter output with a server-held key so clients can detect tampering."
related:
  - "[[FEAT-0002-Cycling-Format-MCP-Hosting]]"
  - "[[PHASE-001-Initial-Launch]]"
---

# VPS-hosted MCP server: security + uptime

## Description
PHASE-001's MCP server runs on Edwin's VPS and is reachable from the public internet at `mcp.your-applications.com/your-trainer`. Two failure modes:

1. **Compromise.** Attacker gains shell on the VPS (via stale package, weak SSH config, dependency CVE in MCP framework). Once in, they can modify the converter library to inject malicious output — e.g. workout files that crash the importing app, route files that exfiltrate location data, locale bundles that inject XSS into apps that don't sanitise. Because the MCP server's output is trusted by downstream clients (Claude Desktop, etc.), the blast radius is the user base of all MCP-aware clients invoking our tools.

2. **Downtime.** Server unreachable. MCP-aware clients get tool-call errors and either fall back to no-data answers or, worse, hallucinated answers. Reputational cost compounds with each high-visibility integration that relies on the server.

The likelihood of compromise is low if standard hosting hygiene is applied. The impact is high because converter output is *trusted*.

## Mitigation
- **Minimum attack surface.** Only port 443 (HTTPS) and port 22 (SSH from Edwin's IPs only) open. All other VPS services bound to localhost.
- **Process isolation.** MCP server runs as a dedicated non-root user (`mcp-cycling`) with `nologin` shell. Read-only access to the library files; no write outside `/tmp`.
- **Dependency hygiene.** Pin all dependencies in the library and MCP wrapper. Dependabot or Renovate enabled; weekly review of security advisories.
- **Auto-patching.** `unattended-upgrades` enabled for the VPS OS — security patches applied automatically.
- **Output signing (optional).** Server holds a private key; signs every converter output with a short HMAC. Clients can verify before importing into apps. Adds friction but high-value for downstream apps that trust our output.
- **Monitoring.** Uptime monitor (TASK-0011). Server logs all tool calls; sudden anomalous-pattern detection (e.g. 10× normal volume from one IP) triggers alert.
- **Documented incident response.** Runbook for: suspected compromise → take server offline, rotate keys, audit logs, redeploy from clean state.

## Notes
The combination of *self-hosted* + *trusted-output* + *public* is the high-impact axis. Mitigations bring the residual risk to acceptable but not zero. Re-evaluate after the first 30 days of operation; consider promoting to a managed host if Edwin's ops bandwidth becomes a bottleneck.
