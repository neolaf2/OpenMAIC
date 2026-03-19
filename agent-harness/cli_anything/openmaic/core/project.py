from __future__ import annotations

from pathlib import Path


def resolve_repo_dir(explicit: str | None = None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()
    return Path.cwd().resolve()


def ensure_repo_dir(path: str | Path) -> Path:
    repo = Path(path).expanduser().resolve()
    package_json = repo / "package.json"
    app_dir = repo / "app"
    if not package_json.exists() or not app_dir.exists():
        raise RuntimeError(f"Not an OpenMAIC repo: {repo}")
    return repo
