from pathlib import Path

import pytest

from cli_anything.openmaic.core.api import OpenMAICClient
from cli_anything.openmaic.core.project import ensure_repo_dir
from cli_anything.openmaic.core.session import SessionStore


def test_session_defaults(tmp_path: Path):
    store = SessionStore(tmp_path / "session.json")
    data = store.load()
    assert data["base_url"] == "http://localhost:3000"
    assert data["last_job_id"] is None


def test_session_update_persists(tmp_path: Path):
    store = SessionStore(tmp_path / "session.json")
    store.update(repo_dir="/tmp/openmaic", last_job_id="abc123")
    data = store.load()
    assert data["repo_dir"] == "/tmp/openmaic"
    assert data["last_job_id"] == "abc123"


def test_ensure_repo_dir_accepts_valid_repo(tmp_path: Path):
    (tmp_path / "package.json").write_text("{}")
    (tmp_path / "app").mkdir()
    assert ensure_repo_dir(tmp_path) == tmp_path.resolve()


def test_ensure_repo_dir_rejects_invalid_repo(tmp_path: Path):
    with pytest.raises(RuntimeError):
        ensure_repo_dir(tmp_path)


def test_generate_classroom_uses_nested_pdf_content(monkeypatch):
    client = OpenMAICClient("http://localhost:3000")
    captured = {}

    def fake_request(method, path, **kwargs):
        captured.update({"method": method, "path": path, **kwargs})
        return {"success": True}

    monkeypatch.setattr(client, "_request", fake_request)
    client.generate_classroom("hello", pdf_text="abc", pdf_images=["img1"])
    body = captured["json_body"]
    assert body["pdfContent"]["text"] == "abc"
    assert body["pdfContent"]["images"] == ["img1"]
