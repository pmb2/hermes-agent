# Changelog

All notable changes to Hermes Agent are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project uses date-based version tags (`vYYYY.M.D`).

---

## [Unreleased]

### Added
- **`/version` slash command** — `/version` now works across CLI, gateway, TUI, and
  desktop, displaying version, platform, and git SHA (#9c1bb8d2c, #30340eae2)
- **Desktop: message history via arrow keys** — arrow up/down navigates previous
  user messages in the desktop composer, integrated with the message queue for
  reliable sequencing (#f94363d1f, #ce5003063)

### Fixed
- **Desktop: IME composition for CJK** — committed IME text is flushed on
  `compositionend` so the send button correctly appears with Chinese, Japanese,
  and Korean input (#8e629b9f3)
- **Desktop: reliable composer message queue** — message queue serialization
  fixed for queued sends (#0cbcc7593)
- **Desktop: macOS updater helper repaired** — self-update error path restored
  (#0c0a70774)
- **Desktop: OAuth path fixes** — `serializeJsonBody` wired into OAuth request
  path; restricted OAuth request header avoided (#be2c64be0, #b8234e759)
- **TUI: clean force-send of queued messages** — force-send no longer leaves
  orphaned queued state (#e375c33f7)

---

## [v2026.6.5] — 2026-06-05

### Added
- **MiniMax-M3 model provider** — native minimax provider now supports MiniMax-M3 with
  1M token context window. Available alongside existing MiniMax models in the
  model picker (#36214)
- **Free tool pool** — entitlement and setup wizard now surface a free tool tier,
  making it visible which tools are available without a subscription (#36153)
- **Desktop app** — Hermes now ships a native desktop application (macOS GUI) with
  self-update support. Installed alongside the CLI entry point (#20059)
- **Windows installer** — GitHub Actions workflow to build and sign a Windows
  installer for the desktop app (#36190)
- **Model picker descriptions** — grouped provider rows now show a short description
  on the group layer, with plain labels on individual members, improving model
  selection UX
- **Kanban goal mode** — `goal_mode` cards now run workers in a `/goal` loop,
  enabling iterative task refinement (#35710)
- **Kanban file attachments** — tasks now support file attachments directly on
  cards (#35395)
- **Kanban image vision** — worker vision can now process images referenced in
  task bodies (#34210)
- **Tool Gateway login-on-select** — backend list always shown; login is deferred
  until a backend is actually selected (#35792)
- **Model catalog refresh every hour** — models now refresh from provider catalogs
  hourly instead of daily (#35756)
- **Claude Opus 4.8** — `claude-opus-4.8` and `claude-opus-4.8-fast` models added
  (#34003)
- **DeepSeek V4 Flash** — `deepseek-v4-flash` model added, with trimmed variants
  and curated provider lists grouped by maker (#35659)
- **OpenRouter session stickiness** — `session_id` passed in `extra_body` for
  consistent routing with OpenRouter providers
- **External context engine host contract** — plugins can now register external
  context engines via a contract interface
- **Memory context exposure** — completed-turn message context exposed to memory
  providers for richer hindsight recall (#5a95fb2e1)
- **Hindsight default recall** — `recall_types` defaults to `observation only`
  for cleaner recall behavior (#490b3e76b)
- **mTLS for MCP servers** — MCP client now supports TLS client certificates
  (mTLS) for HTTP and SSE server connections (#33721)
- **NVIDIA skills hub integration** — NVIDIA/skills catalog added as a trusted
  skills hub tap for community skill discovery
- **Agent retry buffering** — retry and fallback status now buffered and
  surfaced only on terminal failure, reducing noise (#33816)
- **Dashboard admin panel** — full administration dashboard covering MCP
  server management, device pairing, webhook configuration, credential
  management, memory viewer, gateway ops, and system diagnostics (#36704)
- **Blank-slate skills install** — `hermes install --no-skills` flag allows
  installing without built-in skills; opt-out/opt-in controls added to the
  install flow (#36228)
- **Curator skill auto-pruning** — built-in skills are automatically pruned
  after configurable inactivity; usage tracking enabled for all skills to
  inform pruning decisions (#36701)
- **/undo on messaging platforms** — undo now works across all messaging
  platform adapters (Telegram, Discord, Slack, etc.) with parity to CLI/TUI
  behavior (#36699)
- **/undo [N] with prefill** — `/undo 3` backs up N turns with prefill payload
  and soft-delete support, enabling multi-turn corrections (#3f7d1c801)
- **/rewind in TUI** — `/rewind` command wired through TUI command dispatch
  with prefill payload for session-level rewind (#243e836dc)
- **Rewind primitives** — `messages.active` flag and state-based rewind
  infrastructure for session rollback (#3e59be0c4, #31cfa08c6)
- **Quick Setup vs Full Setup explained** — first-time setup menu now explains
  the difference between Quick Setup (Nous Portal) and Full Setup (manual
  config) inline (#36227)

### Changed
- **Setup wizard streamlined** — "Full Setup" no longer includes an Agent
  Settings section. Default `max_turns` changed from 90 → 150, default
  `session_reset` changed from `both` → `none`. Quick Setup now routes
  exclusively through Nous Portal. Vision backend auto-detects from the
  main provider (no separate picker). TTS defaults to Edge with no
  TTS sub-flow in setup. Rotation pool sub-flow removed from model
  section (#35723)
- **`/yolo` in chat** — now correctly enables session bypass instead of
  only setting the env var (#5cbc3fbdc)
- **Model picker unification** — `/model` in-chat and `hermes model` CLI
  now share the same list with disk caching (#3a9bc9d88)
- **Skills catalog expanded** — full ClawHub catalog fetched via sitemap,
  growing from ~200 to 19,932+ skills (#34025, #33748)
- **Desktop build integration** — desktop is now built in the `desktop` stage
  on macOS/Linux (was silently skipped) (#36134)
- **`read_file` gutter** — compact gutter is now the only format; the
  `HERMES_READ_GUTTER` env var has been dropped (#35532)

### Fixed
- **macOS desktop self-update** — locally-built app now relaunches correctly
  after in-place self-update (#36198)
- **Gateway death auto-recovery (TUI)** — session auto-recovers on unexpected
  gateway death with lifecycle breadcrumbs persisted (#35893)
- **Vision image size cap** — embedded images are now capped in size before
  they can wedge a session (#35732)
- **`/voice` over SSH** — voice commands now work over SSH when a sound server
  is reachable (#35719)
- **Anthropic thinking signal handling** — dead thinking signatures are cleanly
  demoted when orphan-strip mutates the latest turn
- **Terminal CWD preservation** — live session CWD preserved in `terminal_tool`;
  ACP `update_cwd` kept authoritative (#7a315bd70)
- **Background wrapper compounding** — `spawn_via_env` background wrappers no
  longer compound-rewrite (#6f8975dcd)
- **Tool output limits** — `tool_output_limits` now re-reads config on every
  call instead of caching stale values (#91a98d151)
- **Streaming tool-call dedup** — tool-call args from cumulative-resend
  providers no longer duplicated (#35718)
- **Cache leaks fixed** — unbounded LRU caches in BlueBubbles (`_guid_cache`)
  and Feishu (`_message_text_cache`) now capped with LRU eviction
- **Curses menu stability** — raw arrow-key escape sequences properly decoded
  in curses menus (#3463c97a3)
- **Terminal dimension clamping** — bogus WSL dimensions (131072×1) now clamped
  in the TUI (#35657)
- **WSL mouse-burst noise** — degraded mouse-burst events can no longer lock
  the TUI composer (#35512)
- **Session survival on gateway stop (Windows)** — `hermes gateway stop` drains
  cleanly so sessions survive restart on Windows (#33798)
- **Gateway restart loops** — self-targeting gateway commands no longer cause
  agent restart loops (#30719)
- **Secret fallback** — tools fall back to `.hermes/.env` when a forwarded
  secret is empty (#35583)
- **Docker UID/GID validation** — privilege escalation in stage2-hook prevented
  via validation (#35340)
- **Telegram DM routing** — topic routing metadata preserved in synthetic
  notifications (#4259bab7d)
- **File path neutralization** — file paths in mutation-verifier footer
  neutralized for security (#35584)
- **Patch unescape** — `\t`/`\r` sequences now unescaped in all match
  strategies for the `patch` tool (#33733)
- **Skills page performance** — catalog now lazy-fetched instead of bundling
  34MB into JS (#33809)
- **Kanban DB corruption** — content-addressed backup filenames prevent
  corrupt-DB overwrite (#6f9182cb3)
- **Content-policy blocks** — agent falls back immediately on provider
  content-policy blocks without delay (#33883)
- **xAI OAuth paste** — bare-code manual paste without state parameter now
  accepted (#33880)
- **Discord thread backfill** — auto-created thread contexts correctly
  backfilled (#eafe11d45)
- **Web dashboard auth loop** — stale-token 401 no longer triggers reload
  loop in loopback mode (#33861)

### Removed
- **Setup Agent Settings section** — Full Setup no longer offers an Agent
  Settings panel (moved to manual `config.yaml` editing) (#35723)
- **Setup rotation pool** — model rotation pool configuration removed from
  setup wizard (#35723)
- **`HERMES_READ_GUTTER` env var** — compact gutter is now the only read_file
  format (#35532)

---

## [v2026.5.29.2] — 2026-05-29

### Fixed
- Stale `patch` tool unescape behavior (widen strategy coverage)

## [v2026.5.29] — 2026-05-29

### Added
- Kanban image attachments for worker vision
- External context engine contract interface
- mTLS support for MCP client
- NVIDIA skills hub integration
- Claude Opus 4.8 and 4.8-fast

### Changed
- Skills catalog expanded to 19,932+ via sitemap fetch
- Model picker unified between `/model` CLI and in-chat

### Fixed
- MCP client now resolves bare npx/npm/node against `/usr/local/bin`
- Kanban SIGTERM properly terminates worker processes
- Skills hub identifier column no longer ellipsis-truncated
- Dashboard auto-reloads on stale-token 401 in loopback mode
- Gateway backfills Discord thread context
- Content-policy blocks trigger immediate fallback
- Patch tool unescape covers all match strategies
- Session survives gateway stop on Windows
- Update command no longer soft-bricks on stalled webui build

---

## [v2026.5.16] — 2026-05-16

### Added
- Kanban toolsets (`kanban`, `session_search`, `todo`) for worker isolation
- `/voice` command over SSH with available sound server
- Claude 4.5 Opus model family
- Session interruption via `/stop` in per-user gateway threads
- Prefix completion mode in TUI composer

### Changed
- Tool backends now shown before login (click to authenticate)
- `read_file` default format changed to compact gutter
- Skills hub catalog refresh rate improved

### Fixed
- TUI composer no longer locked by degraded mouse events
- Session create/delegate race conditions resolved
- MCP tool registration deduplication
- Windows path handling in MEDIA tags
- FTS5 runtime fallback for missing system SQLite
- Update migration prompt now names new config options

---

## [v2026.5.7] — 2026-05-07

### Added
- Kanban boards and task management
- Skill hub integration (community skills)
- MCP server connection pooling
- Provider failover with automatic fallback

### Changed
- Gateway architecture overhaul for multi-platform support
- Config schema v2 migration support

### Fixed
- Memory persistence across sessions
- Tool call deduplication in streaming responses
- GitHub auth token refresh handling
- Nix build reproducibility

---

## [v2026.4.30] — 2026-04-30

### Added
- Initial public release
- Session management with `hermes session`
- Tool gateway with Telegram, Discord, web, and terminal interfaces
- MCP client for external tool integration
- Configurable provider routing
- Skill authoring and auto-inference
- Desktop application (alpha)
- Kanban task management (alpha)
- Windows support (beta)
