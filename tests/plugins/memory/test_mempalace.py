"""Tests for MemPalace memory provider — CLI availability, search parsing, lifecycle.

The real mempalace package and palace directory are NOT required — all
external calls (subprocess, Path.exists) are monkeypatched.
"""

import json
import os
import subprocess
from pathlib import Path

import pytest

from plugins.memory.mempalace import (
    MemPalaceProvider,
    _mempalace_available,
    _palace_exists,
    _search_palace,
    _add_drawer,
)


# ---------------------------------------------------------------------------
# Helper checks
# ---------------------------------------------------------------------------


class TestMempalaceAvailable:
    def test_available_when_subprocess_succeeds(self, monkeypatch):
        def fake_run(*args, **kwargs):
            class FakeResult:
                returncode = 0
            return FakeResult()
        monkeypatch.setattr(subprocess, "run", fake_run)
        assert _mempalace_available() is True

    def test_unavailable_when_subprocess_fails(self, monkeypatch):
        def fake_run(*args, **kwargs):
            class FakeResult:
                returncode = 1
            return FakeResult()
        monkeypatch.setattr(subprocess, "run", fake_run)
        assert _mempalace_available() is False

    def test_unavailable_on_exception(self, monkeypatch):
        def fake_run(*args, **kwargs):
            raise FileNotFoundError("no mempalace")
        monkeypatch.setattr(subprocess, "run", fake_run)
        assert _mempalace_available() is False


class TestPalaceExists:
    def test_exists_when_chromadb_present(self, monkeypatch, tmp_path):
        chroma_dir = tmp_path / ".mempalace" / "palace"
        chroma_dir.mkdir(parents=True)
        (chroma_dir / "chroma.sqlite3").write_text("")
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        assert _palace_exists() is True

    def test_not_exists_when_no_chromadb(self, monkeypatch, tmp_path):
        palace_dir = tmp_path / ".mempalace" / "palace"
        palace_dir.mkdir(parents=True)
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        assert _palace_exists() is False

    def test_not_exists_when_no_palace_dir(self, monkeypatch, tmp_path):
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        assert _palace_exists() is False


# ---------------------------------------------------------------------------
# CLI output parsing
# ---------------------------------------------------------------------------


class TestSearchPalace:
    def test_parses_key_value_lines(self, monkeypatch):
        def fake_run(*args, **kwargs):
            class FakeResult:
                returncode = 0
                stdout = "text: hello world\nscore: 0.95\n\n"
                stderr = ""
            return FakeResult()
        monkeypatch.setattr(subprocess, "run", fake_run)
        results = _search_palace("hello")
        assert len(results) == 1
        assert results[0]["text"] == "hello world"
        assert results[0]["score"] == "0.95"

    def test_handles_multi_line_text(self, monkeypatch):
        def fake_run(*args, **kwargs):
            class FakeResult:
                returncode = 0
                stdout = "text: hello world\nmore context here\n\n"
                stderr = ""
            return FakeResult()
        monkeypatch.setattr(subprocess, "run", fake_run)
        results = _search_palace("hello")
        assert len(results) == 1
        assert "hello world" in results[0]["text"]
        assert "more context here" in results[0].get("text", "")

    def test_returns_empty_on_subprocess_failure(self, monkeypatch):
        def fake_run(*args, **kwargs):
            raise subprocess.TimeoutExpired(cmd="mempalace", timeout=30)
        monkeypatch.setattr(subprocess, "run", fake_run)
        assert _search_palace("hello") == []

    def test_respects_limit(self, monkeypatch):
        def fake_run(*args, **kwargs):
            class FakeResult:
                returncode = 0
                stdout = "text: one\n\n" "text: two\n\n" "text: three\n\n" "text: four\n\n"
                stderr = ""
            return FakeResult()
        monkeypatch.setattr(subprocess, "run", fake_run)
        results = _search_palace("hello", limit=2)
        assert len(results) == 2


# ---------------------------------------------------------------------------
# Provider lifecycle
# ---------------------------------------------------------------------------


class TestMemPalaceProvider:
    def test_initializes_with_env_overrides(self, monkeypatch):
        monkeypatch.setenv("MEMORY_PROVIDER_WING", "custom-wing")
        monkeypatch.setenv("MEMORY_PROVIDER_ROOM", "custom-room")
        provider = MemPalaceProvider()
        provider.initialize("test-session")
        assert provider._session_id == "test-session"
        assert provider._wing == "custom-wing"
        assert provider._room == "custom-room"
        assert provider._initialized is True

    def test_default_wing_and_room(self):
        provider = MemPalaceProvider()
        assert provider._wing == "hermes-memory"
        assert provider._room == "agent-memories"

    def test_is_available_checks_both_cli_and_palace(self, monkeypatch):
        monkeypatch.setattr(
            "plugins.memory.mempalace._mempalace_available",
            lambda: True,
        )
        monkeypatch.setattr(
            "plugins.memory.mempalace._palace_exists",
            lambda: True,
        )
        provider = MemPalaceProvider()
        assert provider.is_available() is True

    def test_is_available_false_when_cli_missing(self, monkeypatch):
        monkeypatch.setattr(
            "plugins.memory.mempalace._mempalace_available",
            lambda: False,
        )
        provider = MemPalaceProvider()
        assert provider.is_available() is False

    def test_name(self):
        assert MemPalaceProvider().name == "mempalace"

    def test_get_tool_schemas(self):
        provider = MemPalaceProvider()
        schemas = provider.get_tool_schemas()
        names = [s["name"] for s in schemas]
        assert "mempalace_search" in names
        assert "mempalace_status" in names


# ---------------------------------------------------------------------------
# Tool call handling
# ---------------------------------------------------------------------------


class TestHandleToolCall:
    def test_search_returns_results(self, monkeypatch):
        def fake_search(query, limit=5):
            return [{"text": "found it", "score": "0.99"}]
        monkeypatch.setattr("plugins.memory.mempalace._search_palace", fake_search)

        provider = MemPalaceProvider()
        result = json.loads(provider.handle_tool_call("mempalace_search", {"query": "test"}))

        assert len(result["results"]) == 1
        assert result["results"][0]["text"] == "found it"

    def test_search_passes_limit(self, monkeypatch):
        captured = {}

        def fake_search(query, limit=5):
            captured["query"] = query
            captured["limit"] = limit
            return []
        monkeypatch.setattr("plugins.memory.mempalace._search_palace", fake_search)

        provider = MemPalaceProvider()
        provider.handle_tool_call("mempalace_search", {"query": "foo", "limit": 3})
        assert captured["query"] == "foo"
        assert captured["limit"] == 3

    def test_unknown_tool_raises(self):
        provider = MemPalaceProvider()
        with pytest.raises(NotImplementedError, match="does not handle tool"):
            provider.handle_tool_call("nonexistent", {})


# ---------------------------------------------------------------------------
# System prompt / lifecycle hooks
# ---------------------------------------------------------------------------


class TestSystemPrompt:
    def test_includes_wing_name(self):
        provider = MemPalaceProvider()
        provider._wing = "custom-wing"
        prompt = provider.system_prompt_block()
        assert "custom-wing" in prompt
        assert "mempalace_search" in prompt
