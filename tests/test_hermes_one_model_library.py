"""Tests for the extracted Hermes One model-library helpers.

Covers the pure helpers moved from ``hermes_cli/web_server.py`` into
``hermes_cli/hermes_one_model_library.py`` (extraction commit, 2026-07-31).
All tests isolate ``HERMES_HOME`` via monkeypatched ``get_hermes_home`` and
``load_config`` — no real config or home directory is touched.
"""

import json

import pytest

from hermes_cli import hermes_one_model_library as lib


@pytest.fixture
def isolated_lib(tmp_path, monkeypatch):
    monkeypatch.setattr(lib, "get_hermes_home", lambda: tmp_path)
    monkeypatch.setattr(lib, "load_config", lambda: {"model": {"provider": "deepseek", "default": "deepseek-v4-flash"}})
    return tmp_path


# --- normalize ---------------------------------------------------------------


def test_normalize_valid_row_defaults():
    row = lib._hermes_one_normalize_model_row({"provider": " openai ", "model": "gpt-4o"})
    assert row["provider"] == "openai"
    assert row["model"] == "gpt-4o"
    assert row["id"] == "remote:library:openai:0:gpt-4o"
    assert row["name"] == "gpt-4o"
    assert row["baseUrl"] == ""
    assert row["createdAt"] == 0


def test_normalize_uses_base_url_fallback_and_preserves_id():
    row = lib._hermes_one_normalize_model_row(
        {"id": "keep-me", "provider": "p", "model": "m", "base_url": "https://x/", "createdAt": 123}
    )
    assert row["id"] == "keep-me"
    assert row["baseUrl"] == "https://x/"
    assert row["createdAt"] == 123


def test_normalize_rejects_missing_fields_and_non_dicts():
    assert lib._hermes_one_normalize_model_row({"provider": "p"}) is None
    assert lib._hermes_one_normalize_model_row({"model": "m"}) is None
    assert lib._hermes_one_normalize_model_row("nope") is None
    assert lib._hermes_one_normalize_model_row(None) is None


# --- keys + labels -----------------------------------------------------------


def test_model_key_normalizes_case_and_base_url():
    a = lib._hermes_one_model_key({"provider": "OpenAI", "model": "GPT-4o", "baseUrl": "https://X/"})
    b = lib._hermes_one_model_key({"provider": "openai", "model": "gpt-4o", "base_url": "https://x"})
    assert a == b


def test_short_model_label_strips_path_prefix():
    assert lib._hermes_one_short_model_label("org/repo/model-name") == "model-name"
    assert lib._hermes_one_short_model_label("") == ""
    assert lib._hermes_one_short_model_label(None) == ""


# --- library read/write roundtrip --------------------------------------------


def test_write_then_read_roundtrip(isolated_lib):
    row = lib._hermes_one_normalize_model_row({"provider": "p", "model": "m"})
    lib._hermes_one_write_model_library([row])
    assert lib._hermes_one_read_model_library() == [row]
    # atomic write leaves no .tmp behind
    assert not (isolated_lib / "models.json.tmp").exists()


def test_read_deduplicates_and_skips_invalid(isolated_lib):
    (isolated_lib / "models.json").write_text(
        json.dumps(
            [
                {"provider": "p", "model": "m"},  # no baseUrl -> key ("p","m","")
                {"provider": "P", "model": "M"},  # duplicate of row 1 after normalize
                {"provider": "q", "model": "n", "baseUrl": "https://x"},
                {"provider": "q", "model": "n", "base_url": "https://x"},  # dup of row 3
                {"provider": "broken"},
            ]
        ),
        encoding="utf-8",
    )
    rows = lib._hermes_one_read_model_library()
    assert len(rows) == 2
    assert {r["provider"] for r in rows} == {"p", "q"}
    assert [r["baseUrl"] for r in rows] == ["", "https://x"]


def test_read_missing_and_corrupt_file_yield_empty(isolated_lib):
    assert lib._hermes_one_read_model_library() == []
    (isolated_lib / "models.json").write_text("{not json", encoding="utf-8")
    assert lib._hermes_one_read_model_library() == []


# --- current model row -------------------------------------------------------


def test_current_model_row_from_config(isolated_lib):
    row = lib._hermes_one_current_model_row()
    assert row["provider"] == "deepseek"
    assert row["model"] == "deepseek-v4-flash"
    assert row["id"] == "remote:active:deepseek:deepseek-v4-flash"
    assert row["createdAt"] == 0


def test_current_model_row_none_when_config_unset(isolated_lib, monkeypatch):
    monkeypatch.setattr(lib, "load_config", lambda: {"model": {}})
    assert lib._hermes_one_current_model_row() is None


def test_current_model_row_handles_scalar_model_and_config_error(isolated_lib, monkeypatch):
    # scalar model string with no provider -> no row (provider required)
    monkeypatch.setattr(lib, "load_config", lambda: {"model": "just-a-string"})
    assert lib._hermes_one_current_model_row() is None
    monkeypatch.setattr(lib, "load_config", lambda: (_ for _ in ()).throw(RuntimeError("boom")))
    assert lib._hermes_one_current_model_row() is None
