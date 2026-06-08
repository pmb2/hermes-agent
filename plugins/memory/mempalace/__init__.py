"""MemPalace memory plugin — MemoryProvider interface.

Uses the local MemPalace palace (ChromaDB + SQLite) for persistent,
fully local memory storage with semantic search. No API key required.

Config via environment variables:
  MEMORY_PROVIDER_WING  — Palace wing for agent memories (default: hermes-memory)
  MEMORY_PROVIDER_ROOM  — Default room within the wing (default: agent-memories)

Requires: mempalace >= 3.3.0 (already installed)
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
import json
import time
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

from agent.memory_provider import MemoryProvider

logger = logging.getLogger(__name__)

_MEMORY_WING = "hermes-memory"
_MEMORY_ROOM = "agent-memories"
_MAX_PREFETCH_RESULTS = 5
_SYNC_BACKOFF_SECS = 1.0

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mempalace_available() -> bool:
    """Check if the mempalace CLI is installed."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "mempalace", "--help"],
            capture_output=True, text=True, timeout=10,
        )
        return result.returncode == 0
    except Exception:
        return False


def _palace_exists() -> bool:
    """Check if a palace has been initialized."""
    palace_dir = Path.home() / ".mempalace" / "palace"
    return palace_dir.exists() and (palace_dir / "chroma.sqlite3").exists()


def _search_palace(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Search the palace via CLI."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "mempalace", "search", query],
            capture_output=True, text=True, timeout=30,
            cwd=str(Path.home()),
        )
        # Parse search results from CLI output
        lines = result.stdout.strip().split("\n")
        results = []
        current = {}
        for line in lines:
            line = line.strip()
            if not line:
                if current:
                    results.append(current)
                    current = {}
                continue
            if ": " in line:
                key, val = line.split(": ", 1)
                current[key.lower().replace(" ", "_")] = val
            else:
                current.setdefault("text", "")
                current["text"] += line + " "
        if current:
            results.append(current)
        return results[:limit]
    except Exception as e:
        logger.warning(f"Palace search failed: {e}")
        return []


def _add_drawer(wing: str, room: str, content: str) -> bool:
    """Add a drawer to the palace via MCP-compatible approach.
    
    Uses the mempalace Python API directly to add content.
    Falls back to the hooks_cli for adding memories.
    """
    try:
        # Use the hooks_cli's add_drawer functionality via internal API
        from mempalace.palace import get_collection
        
        collection = get_collection(f"{wing}/{room}")
        doc_id = f"{wing}_{room}_{int(time.time())}_{hash(content) % 10000}"
        collection.add(
            documents=[content],
            ids=[doc_id],
            metadatas=[{"wing": wing, "room": room, "created": time.time()}],
        )
        return True
    except ImportError:
        pass
    except Exception as e:
        logger.warning(f"Direct add failed ({e}), trying CLI fallback")

    # CLI fallback — add via JSON on stdin
    try:
        # Hooks CLI accepts JSON on stdin
        payload = json.dumps({
            "wing": wing,
            "room": room,
            "content": content,
            "source": "hermes-memory-provider",
            "created": time.time(),
        })
        result = subprocess.run(
            [sys.executable, "-m", "mempalace", "mcp", "add-drawer"],
            input=payload,
            capture_output=True, text=True, timeout=30,
        )
        return result.returncode == 0
    except Exception as e:
        logger.warning(f"CLI add_drawer failed: {e}")
        return False


# ---------------------------------------------------------------------------
# Provider
# ---------------------------------------------------------------------------

class MemPalaceProvider(MemoryProvider):
    """Memory provider backed by local MemPalace (ChromaDB + SQLite)."""

    def __init__(self):
        self._session_id = ""
        self._wing = os.environ.get("MEMORY_PROVIDER_WING", _MEMORY_WING)
        self._room = os.environ.get("MEMORY_PROVIDER_ROOM", _MEMORY_ROOM)
        self._available = False
        self._initialized = False
        self._lock = Lock()
        self._turn_buffer: List[str] = []
        self._kwargs: Dict[str, Any] = {}

    # -- Required properties / methods ---------------------------------------

    @property
    def name(self) -> str:
        return "mempalace"

    def is_available(self) -> bool:
        if not _mempalace_available():
            logger.info("mempalace CLI not available")
            return False
        if not _palace_exists():
            logger.info("MemPalace palace not found at ~/.mempalace/palace/")
            return False
        return True

    def initialize(self, session_id: str, **kwargs) -> None:
        self._session_id = session_id
        self._kwargs = kwargs
        with self._lock:
            self._initialized = True
        logger.info(
            "MemPalace provider initialized for session %s "
            "(wing=%s, room=%s)",
            session_id, self._wing, self._room,
        )

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Expose mempalace search and status as tools."""
        return [
            {
                "name": "mempalace_search",
                "description": (
                    "Search your MemPalace palace for memories, facts, "
                    "and context across all past sessions. Fully local, "
                    "semantic search."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max results",
                            "default": 5,
                        },
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "mempalace_status",
                "description": "Get palace overview — total drawers, wings, rooms.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
        ]

    def handle_tool_call(self, tool_name: str, args: Dict[str, Any], **kwargs) -> str:
        if tool_name == "mempalace_search":
            results = _search_palace(
                args.get("query", ""),
                limit=args.get("limit", 5),
            )
            return json.dumps({"results": results}, indent=2)
        elif tool_name == "mempalace_status":
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "mempalace", "status"],
                    capture_output=True, text=True, timeout=15,
                )
                return result.stdout or json.dumps({"error": "No output"})
            except Exception as e:
                return json.dumps({"error": str(e)})
        raise NotImplementedError(
            f"MemPalace provider does not handle tool {tool_name}"
        )

    # -- Optional lifecycle hooks --------------------------------------------

    def system_prompt_block(self) -> str:
        return (
            "You have local persistent memory via MemPalace. "
            "Use `mempalace_search` to recall past conversations and facts. "
            f"Your memories are stored in the wing '{self._wing}'."
        )

    def prefetch(self, query: str, *, session_id: str = "") -> str:
        """Recall relevant context for the upcoming turn."""
        if not query.strip():
            return ""
        try:
            results = _search_palace(query, limit=_MAX_PREFETCH_RESULTS)
            if not results:
                return ""
            lines = ["[MemPalace recall:]"]
            for r in results:
                text = r.get("text", r.get("content", str(r)))[:300]
                lines.append(f"  - {text}")
            return "\n".join(lines)
        except Exception as e:
            logger.debug(f"prefetch error: {e}")
            return ""

    def sync_turn(
        self,
        user_content: str,
        assistant_content: str,
    ) -> None:
        """Store a turn summary to the palace."""
        # Buffer turns and batch-write to avoid excessive I/O
        batch = None
        with self._lock:
            self._turn_buffer.append(
                f"User: {user_content[:500]}\n"
                f"Assistant: {assistant_content[:500]}"
            )
            if len(self._turn_buffer) >= 5:
                batch = list(self._turn_buffer)
                self._turn_buffer.clear()

        # Store (async in background would be better, but for now sync)
        if batch:
            try:
                for entry in batch:
                    _add_drawer(
                        self._wing,
                        self._room,
                        f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {entry}",
                    )
            except Exception:
                pass

    def on_memory_write(
        self,
        action: str,
        target: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Mirror built-in memory writes to the palace."""
        try:
            _add_drawer(
                self._wing,
                f"{self._room}/memory-{target}",
                f"[memory:{action}:{target}] {content[:1000]}",
            )
        except Exception as e:
            logger.debug(f"on_memory_write: {e}")

    def shutdown(self) -> None:
        """Flush remaining buffered turns on shutdown."""
        with self._lock:
            remaining = list(self._turn_buffer)
            self._turn_buffer.clear()
        for entry in remaining:
            try:
                _add_drawer(self._wing, self._room, entry)
            except Exception:
                pass
        logger.info("MemPalace provider shut down")
