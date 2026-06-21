"""Smoke tests for the Hermes One model library helpers.

These test the pure helper functions used by the /api/model/library endpoints
without needing FastAPI/uvicorn. The helper functions are in web_server.py and
provide REST CRUD for remote model shortcuts with atomic writes and dedup.
"""

import json
import time

from hermes_cli.web_server import (
    _hermes_one_short_model_label,
    _hermes_one_model_key,
    _hermes_one_normalize_model_row,
    _hermes_one_write_model_library,
    _hermes_one_read_model_library,
    _hermes_one_current_model_row,
)


# ---------------------------------------------------------------------------
# _hermes_one_short_model_label
# ---------------------------------------------------------------------------

class TestShortModelLabel:
    def test_full_url_returns_tail_segment(self):
        assert _hermes_one_short_model_label(
            "openai/gpt-4o"
        ) == "gpt-4o"

    def test_single_component_returns_as_is(self):
        assert _hermes_one_short_model_label("gpt-4o") == "gpt-4o"

    def test_deep_path_returns_last_segment(self):
        assert _hermes_one_short_model_label(
            "azure/eastus/accounts/llama-3-70b"
        ) == "llama-3-70b"

    def test_none_or_empty_returns_empty_string(self):
        assert _hermes_one_short_model_label(None) == ""
        assert _hermes_one_short_model_label("") == ""

    def test_whitespace_is_stripped(self):
        assert _hermes_one_short_model_label("  openai/gpt-4o  ") == "gpt-4o"

    def test_trailing_slash_returns_full_text_fallback(self):
        # rsplit on "gpt-4o/" -> ['gpt-4o', '']; '' or 'gpt-4o/' = 'gpt-4o/'
        assert _hermes_one_short_model_label("gpt-4o/") == "gpt-4o/"


# ---------------------------------------------------------------------------
# _hermes_one_model_key
# ---------------------------------------------------------------------------

class TestModelKey:
    def test_provider_model_base_url_triple(self):
        row = {"provider": "OpenAI", "model": "GPT-4o", "baseUrl": "https://api.openai.com"}
        key = _hermes_one_model_key(row)
        assert key == ("openai", "gpt-4o", "https://api.openai.com")

    def test_fallback_to_base_url(self):
        row = {"provider": "M", "model": "X", "base_url": "http://host:8080"}
        key = _hermes_one_model_key(row)
        assert key == ("m", "x", "http://host:8080")

    def test_strips_and_lowercases_all_fields(self):
        row = {"provider": "  AZURE ", "model": "Llama-3", "baseUrl": "HTTPS://HOST:443/"}
        key = _hermes_one_model_key(row)
        assert key == ("azure", "llama-3", "https://host:443")

    def test_trailing_slash_stripped_from_base_url(self):
        row = {"provider": "X", "model": "Y", "baseUrl": "https://host/"}
        key = _hermes_one_model_key(row)
        assert key == ("x", "y", "https://host")

    def test_missing_fields_use_empty_strings(self):
        key = _hermes_one_model_key({})
        assert key == ("", "", "")


# ---------------------------------------------------------------------------
# _hermes_one_normalize_model_row
# ---------------------------------------------------------------------------

class TestNormalizeModelRow:
    def test_valid_row_returns_normalized_dict(self):
        row = {"provider": "openai", "model": "gpt-4o", "name": "My GPT", "baseUrl": "https://api.openai.com"}
        result = _hermes_one_normalize_model_row(row, index=0)
        assert result is not None
        assert result["provider"] == "openai"
        assert result["model"] == "gpt-4o"
        assert result["name"] == "My GPT"
        assert result["baseUrl"] == "https://api.openai.com"

    def test_non_dict_returns_none(self):
        assert _hermes_one_normalize_model_row("not a dict") is None

    def test_missing_provider_returns_none(self):
        row = {"model": "gpt-4o", "name": "test"}
        assert _hermes_one_normalize_model_row(row) is None

    def test_missing_model_returns_none(self):
        row = {"provider": "openai", "name": "test"}
        assert _hermes_one_normalize_model_row(row) is None

    def test_empty_provider_returns_none(self):
        row = {"provider": "  ", "model": "gpt-4o"}
        assert _hermes_one_normalize_model_row(row) is None

    def test_name_defaults_to_short_label(self):
        row = {"provider": "openai", "model": "openai/gpt-4o-mini", "name": ""}
        result = _hermes_one_normalize_model_row(row)
        assert result["name"] == "gpt-4o-mini"

    def test_id_generated_if_missing(self):
        row = {"provider": "p", "model": "m"}
        result = _hermes_one_normalize_model_row(row, index=3)
        assert result["id"] == "remote:library:p:3:m"

    def test_id_preserved_if_set(self):
        row = {"provider": "p", "model": "m", "id": "custom:1"}
        result = _hermes_one_normalize_model_row(row)
        assert result["id"] == "custom:1"

    def test_createdAt_preserved_if_valid(self):
        row = {"provider": "p", "model": "m", "createdAt": 1718000000000}
        result = _hermes_one_normalize_model_row(row)
        assert result["createdAt"] == 1718000000000

    def test_createdAt_reset_if_invalid_type(self):
        row = {"provider": "p", "model": "m", "createdAt": "2024-06-10"}
        result = _hermes_one_normalize_model_row(row)
        assert result["createdAt"] == 0

    def test_base_url_fallback_to_base_url_key(self):
        row = {"provider": "p", "model": "m", "base_url": "http://local:8080"}
        result = _hermes_one_normalize_model_row(row)
        assert result["baseUrl"] == "http://local:8080"

    def test_base_url_prefers_baseUrl_over_base_url(self):
        row = {"provider": "p", "model": "m", "baseUrl": "http://primary", "base_url": "http://legacy"}
        result = _hermes_one_normalize_model_row(row)
        assert result["baseUrl"] == "http://primary"


# ---------------------------------------------------------------------------
# _hermes_one_read_model_library / _hermes_one_write_model_library
# ---------------------------------------------------------------------------

class TestReadWriteModelLibrary:
    def test_write_then_read_roundtrip(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "hermes_cli.web_server.get_hermes_home",
            lambda: tmp_path,
        )
        rows = [
            {"provider": "openai", "model": "gpt-4o", "name": "GPT-4o", "id": "m1", "createdAt": 100},
            {"provider": "anthropic", "model": "claude-sonnet-4.6", "name": "Sonnet",
             "baseUrl": "https://api.anthropic.com", "id": "m2", "createdAt": 200},
        ]
        _hermes_one_write_model_library(rows)
        result = _hermes_one_read_model_library()
        assert len(result) == 2
        assert result[0]["provider"] == "openai"
        assert result[1]["provider"] == "anthropic"

    def test_read_deduplicates_by_key(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "hermes_cli.web_server.get_hermes_home",
            lambda: tmp_path,
        )
        rows = [
            {"provider": "openai", "model": "gpt-4o", "id": "dup1"},
            {"provider": "OpenAI", "model": "Gpt-4o", "id": "dup2"},  # duplicate (case-insensitive key)
            {"provider": "openai", "model": "gpt-4o", "id": "dup3"},  # duplicate
        ]
        _hermes_one_write_model_library(rows)
        result = _hermes_one_read_model_library()
        assert len(result) == 1

    def test_atomic_write_replaces_content(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "hermes_cli.web_server.get_hermes_home",
            lambda: tmp_path,
        )
        _hermes_one_write_model_library([{"provider": "a", "model": "v1", "id": "x"}])
        _hermes_one_write_model_library([{"provider": "b", "model": "v2", "id": "y"}])
        result = _hermes_one_read_model_library()
        assert len(result) == 1
        assert result[0]["provider"] == "b"

    def test_read_nonexistent_file_returns_empty_list(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "hermes_cli.web_server.get_hermes_home",
            lambda: tmp_path,
        )
        result = _hermes_one_read_model_library()
        assert result == []

    def test_read_corrupted_file_returns_empty_list(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "hermes_cli.web_server.get_hermes_home",
            lambda: tmp_path,
        )
        models_json = tmp_path / "models.json"
        models_json.write_text("not valid json", encoding="utf-8")
        result = _hermes_one_read_model_library()
        assert result == []

    def test_read_non_list_json_returns_empty_list(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "hermes_cli.web_server.get_hermes_home",
            lambda: tmp_path,
        )
        models_json = tmp_path / "models.json"
        models_json.write_text(json.dumps({"key": "not-a-list"}), encoding="utf-8")
        result = _hermes_one_read_model_library()
        assert result == []

    def test_invalid_rows_are_skipped_during_read(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "hermes_cli.web_server.get_hermes_home",
            lambda: tmp_path,
        )
        _hermes_one_write_model_library([
            {"provider": "valid", "model": "good", "id": "1"},
            {"model": "orphan", "id": "2"},  # missing provider — filtered
            "not_a_dict",                     # non-dict — filtered
        ])
        result = _hermes_one_read_model_library()
        assert len(result) == 1
        assert result[0]["id"] == "1"


# ---------------------------------------------------------------------------
# _hermes_one_current_model_row
# ---------------------------------------------------------------------------

class TestCurrentModelRow:
    def test_returns_correct_model_from_dict_config(self, monkeypatch):
        def _fake_config():
            return {
                "model": {
                    "provider": "openai",
                    "default": "gpt-4o",
                    "base_url": "https://api.openai.com",
                }
            }
        monkeypatch.setattr("hermes_cli.web_server.load_config", _fake_config)
        result = _hermes_one_current_model_row()
        assert result is not None
        assert result["provider"] == "openai"
        assert result["model"] == "gpt-4o"
        assert result["baseUrl"] == "https://api.openai.com"
        assert result["id"] == "remote:active:openai:gpt-4o"
        assert result["name"] == "gpt-4o"
        assert result["createdAt"] == 0

    def test_fallback_to_name_key(self, monkeypatch):
        def _fake_config():
            return {"model": {"provider": "anthropic", "name": "claude-sonnet-4.6"}}
        monkeypatch.setattr("hermes_cli.web_server.load_config", _fake_config)
        result = _hermes_one_current_model_row()
        assert result["model"] == "claude-sonnet-4.6"

    def test_scalar_model_config_returns_none_no_provider(self, monkeypatch):
        # Scalar config like {"model": "some/provider/model"} has no
        # separate provider key — function returns None by design.
        monkeypatch.setattr("hermes_cli.web_server.load_config", lambda: {"model": "some/provider/model"})
        assert _hermes_one_current_model_row() is None

    def test_missing_provider_returns_none(self, monkeypatch):
        def _fake_config():
            return {"model": {"model": "gpt-4o"}}  # no provider key
        monkeypatch.setattr("hermes_cli.web_server.load_config", _fake_config)
        assert _hermes_one_current_model_row() is None

    def test_missing_model_returns_none(self, monkeypatch):
        def _fake_config():
            return {"model": {"provider": "openai"}}
        monkeypatch.setattr("hermes_cli.web_server.load_config", _fake_config)
        assert _hermes_one_current_model_row() is None

    def test_config_load_exception_returns_none(self, monkeypatch):
        def _fake_config():
            raise RuntimeError("config corrupt")
        monkeypatch.setattr("hermes_cli.web_server.load_config", _fake_config)
        assert _hermes_one_current_model_row() is None
