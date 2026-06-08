## Purpose

Owns the plugin system — third-party and first-party extensions that add functionality without modifying Hermes core. Plugins register tools, providers, memory backends, and lifecycle hooks.

## Ownership

- Plugin discovery and loading — auto-scans `~/.hermes/plugins/` and `hermes-agent/plugins/`
- `plugin.yaml` manifest format — name, version, toolsets, hooks, dependencies
- Built-in plugin categories:
  - `model-providers/` — Inference backends (OpenRouter, Anthropic, Gemini, etc.)
  - `memory/` — Memory provider plugins (Honcho, Mem0, Supermemory, etc.)
  - `browser/` — Browser automation providers
  - `kanban/` — Multi-agent board dispatcher + worker
  - `platforms/` — Extra messaging platform adapters
  - `image_gen/`, `video_gen/` — Media generation providers

## Local Contracts

- Plugin tools are discovered automatically — no need to edit `toolsets.py` or `tools/registry.py`
- Each plugin has its own `plugin.yaml` manifest with `toolsets`, `hooks`, and `dependencies`
- Plugin `__init__.py` registers tools via `ctx.register_tool(...)`
- Custom or local-only tools should use the plugin route, not core `tools/`
- Plugins can set `enabled: false` in `config.yaml` to disable without uninstalling

## Work Guidance

- Keep plugins focused — one responsibility per plugin
- Use `check_fn` for availability checks (API keys, binaries, etc.)
- Plugin toolsets can be enabled/disabled independently per profile
- No dependency on internal Hermes modules beyond the public plugin API

## Verification

- `hermes plugins list` — verify plugin is discovered
- `hermes plugins test <name>` — run plugin's self-test if defined

## Child DOX Index

No child AGENTS.md files in this subtree.
