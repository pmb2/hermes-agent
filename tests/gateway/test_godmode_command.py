"""Tests for gateway /godmode command handler.

Characterization tests for the uncommitted ``_handle_godmode_command``
(working tree, Jul 31 2026). Covers arg validation, script resolution,
subprocess execution, and error reporting. Guards the subprocess surface
so the handler can be safely committed.
"""

from subprocess import TimeoutExpired
from unittest.mock import MagicMock, patch

import pytest

from gateway.config import Platform
from gateway.platforms.base import MessageEvent
from gateway.session import SessionSource


def _make_event(text: str = "/godmode") -> MessageEvent:
    source = SessionSource(
        platform=Platform.TELEGRAM,
        user_id="u1",
        chat_id="c1",
        user_name="tester",
        chat_type="dm",
    )
    return MessageEvent(text=text, source=source, message_id="m1")


def _make_runner():
    from gateway.run import GatewayRunner

    return object.__new__(GatewayRunner)


def _completed(stdout: str, rc: int = 0) -> MagicMock:
    proc = MagicMock()
    proc.returncode = rc
    proc.stdout = stdout
    proc.stderr = ""
    return proc


def _install_script(tmp_path) -> None:
    script_dir = tmp_path / "scripts"
    script_dir.mkdir()
    (script_dir / "godmode_toggle.py").write_text("print('ok')\n")


class TestGodmodeArgValidation:
    @pytest.mark.asyncio
    async def test_invalid_args_return_usage(self):
        runner = _make_runner()
        result = await runner._handle_godmode_command(_make_event("/godmode bogus"))
        assert result == "Usage: /godmode [on|off|status]"

    @pytest.mark.asyncio
    async def test_empty_args_default_to_status(self, tmp_path, monkeypatch):
        _install_script(tmp_path)
        monkeypatch.setenv("HERMES_HOME", str(tmp_path))
        runner = _make_runner()
        with patch("subprocess.run", return_value=_completed("status: OFF")):
            result = await runner._handle_godmode_command(_make_event("/godmode"))
        assert "status" in result.lower()

    @pytest.mark.asyncio
    async def test_state_alias_accepted(self, tmp_path, monkeypatch):
        _install_script(tmp_path)
        monkeypatch.setenv("HERMES_HOME", str(tmp_path))
        runner = _make_runner()
        with patch("subprocess.run", return_value=_completed("status: OFF")):
            result = await runner._handle_godmode_command(_make_event("/godmode state"))
        assert "GODMODE status" in result


class TestGodmodeScriptResolution:
    @pytest.mark.asyncio
    async def test_script_missing_returns_setup_hint(self, tmp_path, monkeypatch):
        monkeypatch.setenv("HERMES_HOME", str(tmp_path))  # no scripts/ inside
        # Isolate from the host machine's Windows env: without clearing these,
        # the fallback can resolve the real HERMES_HOME script and the test
        # becomes environment-dependent.
        monkeypatch.delenv("APPDATA", raising=False)
        monkeypatch.delenv("LOCALAPPDATA", raising=False)
        runner = _make_runner()
        result = await runner._handle_godmode_command(_make_event("/godmode status"))
        assert "godmode_toggle.py not found" in result

    @pytest.mark.asyncio
    async def test_script_found_via_hermes_home(self, tmp_path, monkeypatch):
        _install_script(tmp_path)
        monkeypatch.setenv("HERMES_HOME", str(tmp_path))
        runner = _make_runner()
        with patch("subprocess.run", return_value=_completed("GODMODE: OFF")) as run:
            result = await runner._handle_godmode_command(_make_event("/godmode status"))
        assert "GODMODE: OFF" in result
        run.assert_called_once()
        # args passed through to the toggle script
        assert run.call_args.args[0][-1] == "status"


class TestGodmodeAppDataFallback:
    """The fallback must resolve AppData\\Local (where HERMES_HOME/scripts
    lives on Windows) as a sibling of AppData\\Roaming (what APPDATA points
    at), not a child of it. Regression tests for the dead Windows path."""

    @pytest.mark.asyncio
    async def test_script_found_via_localappdata_env(self, tmp_path, monkeypatch):
        monkeypatch.delenv("HERMES_HOME", raising=False)
        monkeypatch.delenv("APPDATA", raising=False)
        local_hermes = tmp_path / "Local" / "hermes"
        script_dir = local_hermes / "scripts"
        script_dir.mkdir(parents=True)
        (script_dir / "godmode_toggle.py").write_text("print('ok')\n")
        # LOCALAPPDATA == <AppData>\Local
        monkeypatch.setenv("LOCALAPPDATA", str(local_hermes.parent))
        runner = _make_runner()
        with patch("subprocess.run", return_value=_completed("GODMODE: OFF")) as run:
            result = await runner._handle_godmode_command(_make_event("/godmode status"))
        assert "GODMODE: OFF" in result
        assert run.call_args.args[0][1] == str(script_dir / "godmode_toggle.py")

    @pytest.mark.asyncio
    async def test_script_found_via_appdata_sibling_local(self, tmp_path, monkeypatch):
        # Windows APPDATA == <AppData>\Roaming; the script lives under
        # <AppData>\Local — a sibling directory, not a child of Roaming.
        monkeypatch.delenv("HERMES_HOME", raising=False)
        monkeypatch.delenv("LOCALAPPDATA", raising=False)
        local_hermes = tmp_path / "Local" / "hermes"
        script_dir = local_hermes / "scripts"
        script_dir.mkdir(parents=True)
        (script_dir / "godmode_toggle.py").write_text("print('ok')\n")
        monkeypatch.setenv("APPDATA", str(tmp_path / "Roaming"))
        runner = _make_runner()
        with patch("subprocess.run", return_value=_completed("GODMODE: OFF")) as run:
            result = await runner._handle_godmode_command(_make_event("/godmode status"))
        assert "GODMODE: OFF" in result
        assert run.call_args.args[0][1] == str(script_dir / "godmode_toggle.py")


class TestGodmodeExecution:
    @pytest.mark.asyncio
    async def test_on_reports_godmode_on(self, tmp_path, monkeypatch):
        _install_script(tmp_path)
        monkeypatch.setenv("HERMES_HOME", str(tmp_path))
        runner = _make_runner()
        with patch("subprocess.run", return_value=_completed("toggled ON")):
            result = await runner._handle_godmode_command(_make_event("/godmode on"))
        assert "GODMODE ON" in result
        assert "toggled ON" in result

    @pytest.mark.asyncio
    async def test_off_reports_godmode_off(self, tmp_path, monkeypatch):
        _install_script(tmp_path)
        monkeypatch.setenv("HERMES_HOME", str(tmp_path))
        runner = _make_runner()
        with patch("subprocess.run", return_value=_completed("toggled OFF")):
            result = await runner._handle_godmode_command(_make_event("/godmode off"))
        assert "GODMODE OFF" in result

    @pytest.mark.asyncio
    async def test_nonzero_returncode_reports_error(self, tmp_path, monkeypatch):
        _install_script(tmp_path)
        monkeypatch.setenv("HERMES_HOME", str(tmp_path))
        runner = _make_runner()
        with patch("subprocess.run", return_value=_completed("", rc=1)):
            result = await runner._handle_godmode_command(_make_event("/godmode on"))
        assert "godmode toggle error (rc=1)" in result

    @pytest.mark.asyncio
    async def test_subprocess_exception_reports_failure(self, tmp_path, monkeypatch):
        _install_script(tmp_path)
        monkeypatch.setenv("HERMES_HOME", str(tmp_path))
        runner = _make_runner()
        with patch("subprocess.run", side_effect=TimeoutExpired("godmode_toggle.py", 30)):
            result = await runner._handle_godmode_command(_make_event("/godmode on"))
        assert "godmode toggle failed" in result
