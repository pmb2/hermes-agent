## Purpose

Owns the built-in tool system — tool registration, schema collection, availability checking, and dispatch. Tools are auto-discovered from `tools/*.py` and registered via the registry.

## Ownership

- `registry.py` — Central tool registry (register, discover, schema collection, dispatch)
- `tools/*.py` — Individual tool implementations (one file per tool or tool group)
- `environments/` — Terminal backends (local, docker, ssh, modal, daytona, singularity)
- Availability check functions per tool (`check_requirements`)
- Tool state files: use `get_hermes_home()` for profile-aware paths

## Local Contracts

- Each tool file calls `registry.register()` at import time — no manual import list
- All handlers MUST return a JSON string
- Tools declare `requires_env` for required API keys/env vars
- Agent-level tools (todo, memory) are intercepted by `run_agent.py` before `handle_function_call()`
- A tool is only exposed to an agent if its name appears in a toolset (in `toolsets.py`)
- Path references in tool schemas should use `display_hermes_home()` for profile-awareness
- State files should use `get_hermes_home()` — never `Path.home() / ".hermes"`

## Work Guidance

- Prefer the plugin route for custom/local tools — edit `tools/` only for core Hermes tools
- Built-in/core tools: create `tools/your_tool.py` + add to `toolsets.py`
- Follow the registry pattern (see existing tools for exact structure)

## Verification

- `hermes tools list` — verify tool appears in the correct toolset
- Test tool directly via slash command or agent call

## Child DOX Index

- `environments/` — Terminal backends (local, docker, ssh, modal, daytona, singularity)
