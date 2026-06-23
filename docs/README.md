# Hermes Agent Documentation

> Architecture guides, design proposals, and operational references for Hermes Agent internals.

## Top-Level Documents

| Document | Description |
|----------|-------------|
| `session-lifecycle.md` | Full lifecycle of a session: initialization, context management, compression, termination |
| `chronos-managed-cron-contract.md` | Design and contract for Chronos — Hermes' managed cron job system |
| `relay-connector-contract.md` | Connector contract for NeMo Relay integration |
| `rca-ssl-cacert-post-git-pull.md` | Root-cause analysis: SSL cert failures after git operations |
| `hermes-kanban-v1-spec.pdf` | Kanban board v1 specification (PDF) |

## Subdirectories

| Directory | Content |
|-----------|---------|
| `design/` | Design proposals — `profile-builder.md` (dashboard-native profile creation) |
| `kanban/` | Kanban deployment docs — `multi-gateway.md` (concurrent gateway deployment) |
| `middleware/` | Middleware system — request rewriting, execution wrappers, plugin surface |
| `observability/` | Observer hooks — read-only telemetry contract (traces, metrics, audit) |
| `plans/` | Implementation plans — e.g., Telegram stream overflow fix |
| `security/` | Security docs — network egress isolation patterns |

## Related Docs

- [Website Docs](/website/docs/) — user-facing getting-started, guides, and reference
- [AGENTS.md](/AGENTS.md) — development guide and contribution rubric
