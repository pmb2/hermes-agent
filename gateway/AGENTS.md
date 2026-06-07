## Purpose

Owns the messaging gateway subsystem — connects Hermes to external platforms (Telegram, Discord, Slack, etc.) and routes messages between users and AIAgent sessions.

## Ownership

- `run.py` — Gateway runtime loop, connection management, slash command dispatch
- `session.py` — Session lifecycle per chat/thread
- `platforms/` — Platform adapters (one per platform: telegram, discord, slack, signal, matrix, etc.)
- `config.py` — Gateway-specific config loading
- `delivery.py` — Message delivery routing
- `hooks.py` — Gateway lifecycle hooks
- `SPACEBAR.md` — Spacebar / custom Discord-API configuration guide

## Local Contracts

- Add a new platform: create a new file in `platforms/` following the existing adapter pattern (see `ADDING_A_PLATFORM.md`)
- Slash commands must be registered in both `hermes_cli/commands.py` and dispatched in `gateway/run.py`
- Gateway uses direct YAML load for config (not `load_cli_config()`)
- Platform adapters implement the `PlatformAdapter` protocol with `send_message`, `send_media`, etc.
- Worker processes per platform are long-lived and may restart independently

## Work Guidance

- Keep platform adapters thin — business logic belongs in the core agent, not in platform glue
- Handle reconnection gracefully — platforms disconnect; the gateway should retry with backoff
- All platform adapters must check `DISCORD_AUTO_THREAD` and `GATEWAY_ALLOW_ALL_USERS` config flags

## Verification

- `hermes gateway` — test the gateway starts and connects to configured platforms
- Platform-specific: send a test message to each connected platform after changes

## Child DOX Index

No child AGENTS.md files in this subtree.
