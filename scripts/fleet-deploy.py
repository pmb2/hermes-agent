#!/usr/bin/env python
"""
Fleet Deploy — launches per-profile Hermes gateways as detached Windows processes.

Each profile with a DISCORD_BOT_TOKEN (Spacebar JWT) gets its own gateway
process that connects to the Spacebar instance at gc.backus.agency.

Usage:
    python scripts/fleet-deploy.py              # Start fleet
    python scripts/fleet-deploy.py --status     # Show running gateways
    python scripts/fleet-deploy.py --stop       # Kill all fleet gateways

Dependencies:
    - Hermes Agent installed at ~/AppData/Local/hermes/hermes-agent/
    - Profile .env files with DISCORD_BOT_TOKEN + SPACEBAR_API_BASE
"""

import argparse
import json
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path

HERMES_HOME = Path.home() / "AppData" / "Local" / "hermes"
AGENT_DIR = HERMES_HOME / "hermes-agent"
VENV_PYTHON = AGENT_DIR / "venv" / "Scripts" / "python.exe"
VENV_HERMES = AGENT_DIR / "venv" / "Scripts" / "hermes.exe"
# Fallback to python -m hermes_cli.main
FALLBACK_PYTHON = AGENT_DIR / "venv" / "Scripts" / "python.exe"

# Windows detach flags
DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200
CREATE_NO_WINDOW = 0x08000000
DETACH_FLAGS = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW

FLEET_LOG = HERMES_HOME / "fleet-deploy.log"

# Profiles to SKIP (no Spacebar token, or "real" Discord only)
SKIP_PROFILES = {"paul", "scribe-dev"}


def log(msg: str) -> None:
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    FLEET_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(FLEET_LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def find_profiles() -> list[dict]:
    """Scan all profiles and return ones with Spacebar tokens."""
    profiles_dir = HERMES_HOME / "profiles"
    result = []
    for p_dir in sorted(profiles_dir.iterdir()):
        if not p_dir.is_dir():
            continue
        name = p_dir.name
        if name in SKIP_PROFILES:
            continue

        env_file = p_dir / ".env"
        if not env_file.exists():
            continue

        env_content = env_file.read_text(encoding="utf-8")
        token = re.search(r"^DISCORD_BOT_TOKEN=(.+)$", env_content, re.M)
        spacebar = re.search(r"^SPACEBAR_API_BASE=(\S+)", env_content, re.M)

        if token and spacebar:
            result.append({
                "name": name,
                "path": p_dir,
                "token_prefix": token.group(1)[:20],
                "spacebar_url": spacebar.group(1),
            })
    return result


def profile_env(name: str) -> dict:
    """Load .env vars for a profile, returning a clean dict."""
    env = os.environ.copy()
    env_file = HERMES_HOME / "profiles" / name / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    # Pin Hermes home for this profile
    env["HERMES_HOME"] = str(HERMES_HOME / "profiles" / name)
    env["_HERMES_GATEWAY"] = "1"
    return env


def get_running_gateways() -> dict[str, int]:
    """Return {profile_name: pid} for currently running profile gateways."""
    running = {}
    for p_dir in HERMES_HOME.glob("profiles/*/gateway.pid"):
        name = p_dir.parent.name
        try:
            pid = int(p_dir.read_text().strip())
            # Check if process exists
            try:
                os.kill(pid, 0)
                running[name] = pid
            except OSError:
                # Stale PID
                p_dir.unlink(missing_ok=True)
        except (ValueError, OSError):
            pass
    return running


def kill_fleet(profiles: list[dict], hard: bool = False) -> None:
    """Kill all running profile gateways."""
    running = get_running_gateways()
    if not running:
        log("No running fleet gateways found")
        return

    for name, pid in running.items():
        log(f"Stopping {name} (pid {pid})...")
        try:
            if sys.platform == "win32":
                flags = ["/T", "/F"] if hard else []
                subprocess.run(
                    ["taskkill", "/PID", str(pid)] + flags,
                    capture_output=True, timeout=10,
                )
            else:
                sig = signal.SIGKILL if hard else signal.SIGTERM
                os.kill(pid, sig)
        except Exception as e:
            log(f"  Error killing {name} pid {pid}: {e}")

        # Clean PID file
        pid_file = HERMES_HOME / "profiles" / name / "gateway.pid"
        pid_file.unlink(missing_ok=True)

    time.sleep(2)
    still_running = get_running_gateways()
    if still_running:
        log(f"  {len(still_running)} processes still running: {list(still_running.keys())}")
    else:
        log("All fleet gateways stopped")


def start_profile_gateway(profile: dict) -> int | None:
    """Start a gateway for one profile as a detached process. Returns PID or None."""
    name = profile["name"]
    log(f"Starting {name}...")

    # Ensure no stale lock from this profile
    lock_file = profile["path"] / "gateway.lock"
    pid_file = profile["path"] / "gateway.pid"
    pid_file.unlink(missing_ok=True)

    # Build the command
    cmd = [
        str(VENV_PYTHON),
        "-m", "hermes_cli.main",
        "--profile", name,
        "gateway", "run", "--replace",
    ]

    if not cmd[0].exists():
        cmd[0] = str(FALLBACK_PYTHON)

    _hermes_exe = AGENT_DIR / "venv" / "Scripts" / "hermes.exe"
    if _hermes_exe.exists():
        cmd = [str(_hermes_exe), "--profile", name, "gateway", "run", "--replace"]

    env = profile_env(name)

    try:
        proc = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=DETACH_FLAGS,
            cwd=str(AGENT_DIR),
        )
        pid = proc.pid
        log(f"  Launched {name} (pid {pid})")
        return pid
    except Exception as e:
        log(f"  FAILED to start {name}: {e}")
        return None


def show_status() -> None:
    """Display current fleet status."""
    profiles = find_profiles()
    running = get_running_gateways()
    hermes_lock = HERMES_HOME / "gateway.lock"

    print(f"\n{'Profile':<25} {'Token':<22} {'Status':<12} PID")
    print("-" * 75)

    running_count = 0
    for p in profiles:
        name = p["name"]
        token_short = p["token_prefix"][:20] + "..."
        if name in running:
            status = "RUNNING"
            pid = running[name]
            running_count += 1
        else:
            status = "STOPPED"
            pid = "-"
        print(f"{name:<25} {token_short:<22} {status:<12} {pid}")

    print(f"\n{len(profiles)} Spacebar profiles, {running_count} running")

    # Also show main gateway status
    if hermes_lock.exists():
        try:
            lock_data = json.loads(hermes_lock.read_text())
            print(f"\nMain gateway lock: pid={lock_data.get('pid')}")
        except:
            print(f"\nMain gateway lock exists (stale)")


def stop_fleet() -> None:
    """Stop all fleet gateways."""
    profiles = find_profiles()
    log(f"Stopping fleet ({len(profiles)} profiles)...")
    kill_fleet(profiles)
    log("Fleet stop complete")


def deploy_fleet() -> None:
    """Deploy the full fleet."""
    profiles = find_profiles()
    log(f"Deploying fleet: {len(profiles)} profiles with Spacebar tokens")
    log(f"Python: {VENV_PYTHON}")
    log(f"Agent: {AGENT_DIR}")

    # Kill any existing fleet first
    kill_fleet(profiles)

    # Small pause for cleanup
    time.sleep(1)

    # Start each profile
    started = 0
    failed = 0
    for p in profiles:
        pid = start_profile_gateway(p)
        if pid:
            started += 1
            # Small stagger to avoid thundering herd on Spacebar
            time.sleep(0.5)
        else:
            failed += 1

    log(f"\nFleet deploy summary: {started} started, {failed} failed")

    # Wait a moment then show status
    time.sleep(3)
    show_status()


def main():
    parser = argparse.ArgumentParser(description="Hermes Fleet Deploy — Spacebar Multi-Profile Gateway Launcher")
    parser.add_argument("--status", action="store_true", help="Show fleet status")
    parser.add_argument("--stop", action="store_true", help="Stop all fleet gateways")
    parser.add_argument("--list", action="store_true", help="List profiles with Spacebar tokens")

    args = parser.parse_args()

    if args.status:
        show_status()
    elif args.stop:
        stop_fleet()
    elif args.list:
        profiles = find_profiles()
        print(f"Found {len(profiles)} profiles with Spacebar tokens:\n")
        for p in profiles:
            print(f"  {p['name']:<25} → {p['spacebar_url']}")
    else:
        deploy_fleet()


if __name__ == "__main__":
    main()
