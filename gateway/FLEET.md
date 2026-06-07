# ⚕ Hermes Fleet — Spacebar Native Multi-Profile Deployment

## Architecture

Each Hermes profile represents a bot identity on Spacebar (Discord-compatible
self-hosted server at `gc.backus.agency`). Each profile has its own `.env` with:

- `DISCORD_BOT_TOKEN` — Spacebar JWT token (acts as Discord-compatible auth)
- `SPACEBAR_API_BASE` — `https://gc.backus.agency/api/v9`

The adapter (`plugins/platforms/discord/adapter.py`) reads the Spacebar base
URL from the gateway config, patches `discord.http.Route.BASE` before bot
creation, and uses `_discord_api_url()` for standalone sends — **no wrapper
scripts needed**.

## Quick Start

### Single Profile (default)

`hermes gateway run`

This starts the gateway for the active (default) profile, connects its Discord
platform to Spacebar at `gc.backus.agency`, and begins listening.

### Profile-Specific

`hermes -p chief-of-staff gateway run`
`hermes -p forge gateway run`
`hermes -p sentry gateway run`

Each profile gets its own gateway process with its own bot identity.

### Fleet Deploy Script

For launching multiple profiles simultaneously as detached Windows processes:

```bash
python scripts/fleet-deploy.py          # Deploy fleet
python scripts/fleet-deploy.py --status # Show status
python scripts/fleet-deploy.py --stop   # Stop all
python scripts/fleet-deploy.py --list   # List profiles
```

## Profiles Overview

43 profiles with Spacebar tokens, 2 Discord-native (paul, scribe-dev).

## Deployment Files

| File | Purpose |
|------|---------|
| `gateway/SPACEBAR.md` | Full Spacebar deployment documentation |
| `plugins/platforms/discord/adapter.py` | Native Spacebar adapter |
| `gateway/config.py` | Env var to config bridge |
| `scripts/fleet-deploy.py` | Multi-profile fleet launcher |

## Troubleshooting

**Gateway fails to start:**
Check logs: `cat ~/AppData/Local/hermes/gateway-startup.log | tail -50`
Check gateway log: `cat ~/AppData/Local/hermes/logs/gateway.log | tail -50`

**Bot not appearing online:**
- Verify the JWT token in `profiles/<name>/.env` is valid
- Restart: `hermes -p <name> gateway run --replace`

**Stale lock files (Windows):**
- Restart the machine to release orphaned file locks
- Or use `python scripts/fleet-deploy.py --stop`
