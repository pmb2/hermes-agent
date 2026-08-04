"""Tests for the gateway lifecycle guard's referenced-script scanning.

Regression (2026-08-04): commit ``d8b041e58`` wired ``read_remote_script``
into the guard. The terminal-tool fallback (``_read_script_in_env``) decodes
referenced *binary* executables (e.g. ``venv/Scripts/python.exe``, a 45 KB
PE file) with ``errors="replace"``. NUL bytes are valid UTF-8, so they
survive the decode and land in the decoded "text"; the recursive scan then
tokenizes machine code into paths with embedded NUL characters and
``os.open`` raises ``ValueError: embedded null character in path`` (only
``OSError`` was caught) — crashing every terminal command whose executable
token contains a path separator in gateway/cron sessions.
"""

import pytest

from cron import lifecycle_guard as lg

# PE-ish binary payload whose UTF-16LE string decodes (errors="replace") to a
# forward-slash path with literal NUL characters — the exact crash trigger.
_UTF16_PATH = (
    b"C\x00:\x00/\x00U\x00s\x00e\x00r\x00s\x00/\x00b\x00i\x00n\x00/\x00x\x00\x00\x00"
)
_BINARY_GARBAGE = b"MZ\x90\x00\x03\x00\x00\x00" + _UTF16_PATH + b"\x00\x00\x00lib\x00python.dll"


def test_binary_garbage_from_read_remote_callback_does_not_crash_guard(tmp_path):
    """The guard must never crash when a read_remote_script fallback returns
    decoded binary garbage containing literal NUL bytes (#78372)."""
    def fallback(script_path: str):
        return _BINARY_GARBAGE.decode("utf-8", errors="replace")

    command = "./scripts/run.sh --deploy"
    result = lg.contains_gateway_lifecycle_command_or_referenced_script(
        command, cwd=str(tmp_path), read_remote_script=fallback
    )
    assert result is False


def test_binary_garbage_with_lifecycle_shaped_text_is_still_skipped(tmp_path):
    """Even garbage that happens to look like a lifecycle command must be
    treated as binary noise, not as a real referenced script."""
    payload = _BINARY_GARBAGE + b"\x00hermes\x00gateway\x00restart\x00"

    def fallback(script_path: str):
        return payload.decode("utf-8", errors="replace")

    command = "./scripts/run.sh --deploy"
    result = lg.contains_gateway_lifecycle_command_or_referenced_script(
        command, cwd=str(tmp_path), read_remote_script=fallback
    )
    assert result is False


def test_read_local_script_text_skips_binary_with_nul_bytes(tmp_path):
    """Root-cause fix: the local script reader must not decode binaries —
    NUL bytes survive errors='replace' and poison the recursive scan."""
    from tools.terminal_tool import _read_local_script_text

    binary = tmp_path / "tool.exe"
    binary.write_bytes(b"MZ\x90\x00\x03\x00\x00\x00C:\\Windows\\system32\\x.dll\x00")
    assert _read_local_script_text(str(binary), str(tmp_path)) is None


def test_read_local_script_text_returns_text_for_plain_script(tmp_path):
    """Plain text scripts still resolve through the extracted helper."""
    from tools.terminal_tool import _read_local_script_text

    script = tmp_path / "run.sh"
    script.write_bytes(b"#!/bin/sh\necho hi\n")
    assert _read_local_script_text(str(script), str(tmp_path)) == "#!/bin/sh\necho hi\n"
