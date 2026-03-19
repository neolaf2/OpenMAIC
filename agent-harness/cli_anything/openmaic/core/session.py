from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_SESSION_DIR = Path.home() / ".cli-anything-openmaic"
DEFAULT_SESSION_PATH = DEFAULT_SESSION_DIR / "session.json"
DEFAULT_PID_PATH = DEFAULT_SESSION_DIR / "openmaic-dev.pid"


class SessionStore:
    def __init__(self, path: Path | None = None):
        self.path = path or DEFAULT_SESSION_PATH
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {
                "repo_dir": None,
                "base_url": "http://localhost:3000",
                "pid_file": str(DEFAULT_PID_PATH),
                "last_job_id": None,
                "last_poll_url": None,
                "last_pdf_path": None,
                "last_requirement": None,
            }
        return json.loads(self.path.read_text())

    def save(self, data: dict[str, Any]) -> dict[str, Any]:
        self.path.write_text(json.dumps(data, indent=2, sort_keys=True))
        return data

    def update(self, **kwargs: Any) -> dict[str, Any]:
        data = self.load()
        data.update(kwargs)
        return self.save(data)
