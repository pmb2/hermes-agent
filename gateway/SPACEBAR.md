# Spacebar / Custom Discord-API Gateway

The Hermes Discord adapter can connect to **any Discord-compatible API** (Spacebar,
Fosscord, Revolt, etc.) by setting two environment variables in the profile's
`.env` file. No wrapper scripts needed.

## How It Works

The adapter patches discord.py's HTTP route base at connect time:

1. `load_gateway_config()` reads `SPACEBAR_API_BASE` (or `DISCORD_API_BASE`) from env
   and injects it into the discord platform config's `extra.base_url` along with
   the API version (default: v9).
2. `DiscordAdapter.connect()` reads `extra.base_url` / `extra.api_version` from its
   `PlatformConfig` and patches `discord.http.Route.BASE` before creating the Bot.
3. All hardcoded API URLs (`_standalone_send`, forum thread creation) were replaced
   with `_discord_api_url()` which respects the Route.BASE override.

## Per-Profile Configuration

Each fleet profile needs two env vars in its `.env`:

```env
# Spacebar bot JWT token
DISCORD_BOT_TOKEN=<jwt>

# Spacebar API base URL (v9, not v10)
SPACEBAR_API_BASE=https://gc.backus.agency/api/v9

# Optional: WebSocket gateway URL (auto-resolved from /gateway endpoint)
SPACEBAR_WS_URL=wss://gc.backus.agency/
```

When the gateway starts under that profile, it:
- Uses the **Spacebar JWT** for authentication (not the Discord Bot token)
- Connects to `https://gc.backus.agency/api/v9` for REST API calls
- Resolves the WebSocket gateway from `GET /gateway`

## API Version

Spacebar uses API **v9** (the last version Spacebar forked from Discord). The
default `api_version` is `9` when `SPACEBAR_API_BASE` is set. Override with:

```env
SPACEBAR_API_VERSION=9
```

## Verification

```bash
source profiles/<name>/.env
python -c "
from gateway.config import load_gateway_config
cfg = load_gateway_config()
for p, pc in cfg.platforms.items():
    if p.value == 'discord':
        e = pc.extra or {}
        print(f'{p.value}: token={pc.token[:20]}... base_url={e.get(\"base_url\")} v={e.get(\"api_version\")}')
"
```

Expected output:
```
discord: token=eyJhbG... base_url=https://gc.backus.agency/api/v9 api_version=9
```

## What Was Changed

| File | Change |
|------|--------|
| `plugins/platforms/discord/adapter.py` | Added `_api_base_url`, `_api_version`, `_api_url()` to adapter class |
| `plugins/platforms/discord/adapter.py` | Added `_discord_api_url()` standalone helper (Route.BASE + env fallback) |
| `plugins/platforms/discord/adapter.py` | Patches `Route.BASE` before `commands.Bot()` creation, restores after |
| `plugins/platforms/discord/adapter.py` | Replaced 4 hardcoded `https://discord.com/api/v10` URLs in `_standalone_send` |
| `gateway/config.py` | Env var support: `DISCORD_API_BASE` / `SPACEBAR_API_BASE` in `load_gateway_config()` |
