import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def _resolve_cli(name):
    force = os.environ.get("CLI_ANYTHING_FORCE_INSTALLED", "").strip() == "1"
    path = shutil.which(name)
    if path:
        print(f"[_resolve_cli] Using installed command: {path}")
        return [path]
    if force:
        raise RuntimeError(f"{name} not found in PATH. Install with: pip install -e .")
    module = name.replace("cli-anything-", "cli_anything.") + "." + name.split("-")[-1] + "_cli"
    print(f"[_resolve_cli] Falling back to: {sys.executable} -m {module}")
    return [sys.executable, "-m", module]


class TestCLISubprocess:
    CLI_BASE = _resolve_cli("cli-anything-openmaic")
    REPO = "/Users/rich/.openclaw/workspace/OpenMAIC"
    PDF = "/Users/rich/.openclaw/media/inbound/Ai_x-key-method---199944db-971d-46af-985b-5c034973ef6b.pdf"

    def _run(self, args, check=True):
        return subprocess.run(self.CLI_BASE + ["--repo", self.REPO] + args, capture_output=True, text=True, check=check)

    def test_help(self):
        result = self._run(["--help"])
        assert result.returncode == 0
        assert "server" in result.stdout

    def test_health_json(self):
        result = self._run(["--json", "health"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["success"] is True

    def test_pdf_parse_json(self):
        result = self._run(["--json", "pdf", "parse", self.PDF])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["success"] is True
        assert len(data["data"]["text"]) > 100
        print(f"\n  Parsed PDF: {self.PDF} ({len(data['data']['text'])} chars)")

    def test_classroom_generate_submission_json(self):
        result = self._run([
            "--json",
            "classroom",
            "generate",
            "-r",
            "Generate a short Chinese classroom about AI learning methods",
            "-p",
            self.PDF,
        ])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "success" in data
        if data.get("success") is True:
            job_id = data.get("jobId") or data.get("data", {}).get("jobId")
            assert job_id
            print(f"\n  Classroom job: {job_id}")
