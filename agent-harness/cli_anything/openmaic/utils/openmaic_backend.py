from __future__ import annotations

import os
import signal
import subprocess
import time
from pathlib import Path
from typing import Any

from cli_anything.openmaic.core.api import OpenMAICClient


class OpenMAICBackend:
    def __init__(self, repo_dir: str | Path, base_url: str, pid_file: str | Path):
        self.repo_dir = Path(repo_dir).expanduser().resolve()
        self.base_url = base_url.rstrip("/")
        self.pid_file = Path(pid_file).expanduser().resolve()
        self.client = OpenMAICClient(self.base_url)

    def _read_pid(self) -> int | None:
        if not self.pid_file.exists():
            return None
        try:
            return int(self.pid_file.read_text().strip())
        except Exception:
            return None

    def _is_pid_alive(self, pid: int | None) -> bool:
        if not pid:
            return False
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False

    def status(self) -> dict[str, Any]:
        pid = self._read_pid()
        alive = self._is_pid_alive(pid)
        health = None
        try:
            health = self.client.health()
        except Exception as e:
            health = {"success": False, "error": str(e)}
        return {
            "repo_dir": str(self.repo_dir),
            "base_url": self.base_url,
            "pid": pid,
            "pid_alive": alive,
            "health": health,
        }

    def start_dev(self) -> dict[str, Any]:
        existing = self._read_pid()
        if self._is_pid_alive(existing):
            return {"started": False, "already_running": True, "pid": existing, "base_url": self.base_url}
        self.pid_file.parent.mkdir(parents=True, exist_ok=True)
        log_path = self.pid_file.with_suffix(".log")
        with open(log_path, "ab") as log:
            proc = subprocess.Popen(
                ["pnpm", "dev"],
                cwd=str(self.repo_dir),
                stdout=log,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
        self.pid_file.write_text(str(proc.pid))
        return {"started": True, "pid": proc.pid, "base_url": self.base_url, "log_file": str(log_path)}

    def stop(self) -> dict[str, Any]:
        pid = self._read_pid()
        if not pid or not self._is_pid_alive(pid):
            return {"stopped": False, "reason": "not-running", "pid": pid}
        os.killpg(pid, signal.SIGTERM)
        for _ in range(20):
            if not self._is_pid_alive(pid):
                break
            time.sleep(0.2)
        alive = self._is_pid_alive(pid)
        if not alive and self.pid_file.exists():
            self.pid_file.unlink()
        return {"stopped": not alive, "pid": pid, "force_required": alive}
