from __future__ import annotations

import json
import shlex
import sys
import time
from pathlib import Path

import click

from cli_anything.openmaic import __version__
from cli_anything.openmaic.core.api import OpenMAICClient
from cli_anything.openmaic.core.project import ensure_repo_dir, resolve_repo_dir
from cli_anything.openmaic.core.session import SessionStore
from cli_anything.openmaic.utils.openmaic_backend import OpenMAICBackend
from cli_anything.openmaic.utils.repl_skin import ReplSkin


PASS_CTX = click.make_pass_decorator(dict, ensure=True)


def emit(data, as_json: bool):
    if as_json:
        click.echo(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        if isinstance(data, dict):
            for key, value in data.items():
                click.echo(f"{key}: {value}")
        else:
            click.echo(data)


@click.group(invoke_without_command=True)
@click.option("--repo", "repo_dir", type=click.Path(file_okay=False, path_type=Path), help="Path to OpenMAIC repo")
@click.option("--url", "base_url", default=None, help="OpenMAIC base URL")
@click.option("--json", "as_json", is_flag=True, help="Emit machine-readable JSON")
@click.pass_context
def cli(ctx, repo_dir: Path | None, base_url: str | None, as_json: bool):
    ctx.ensure_object(dict)
    session = SessionStore()
    state = session.load()
    resolved_repo = None
    if repo_dir is not None:
        resolved_repo = ensure_repo_dir(repo_dir)
        state = session.update(repo_dir=str(resolved_repo))
    elif state.get("repo_dir"):
        resolved_repo = ensure_repo_dir(state["repo_dir"])
    else:
        try:
            resolved_repo = ensure_repo_dir(resolve_repo_dir())
            state = session.update(repo_dir=str(resolved_repo))
        except Exception:
            resolved_repo = None
    if base_url:
        state = session.update(base_url=base_url)
    ctx.obj.update({
        "session": session,
        "state": state,
        "repo_dir": resolved_repo,
        "base_url": base_url or state.get("base_url") or "http://localhost:3000",
        "as_json": as_json,
    })
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


def _client(ctx_obj: dict) -> OpenMAICClient:
    return OpenMAICClient(ctx_obj["base_url"])


def _backend(ctx_obj: dict) -> OpenMAICBackend:
    repo_dir = ctx_obj.get("repo_dir")
    if repo_dir is None:
        raise click.ClickException("OpenMAIC repo path is required. Pass --repo or run inside the repo.")
    pid_file = ctx_obj["state"].get("pid_file")
    return OpenMAICBackend(repo_dir, ctx_obj["base_url"], pid_file)


@cli.command()
@PASS_CTX
def repl(ctx_obj: dict):
    skin = ReplSkin("openmaic", version=__version__)
    skin.print_banner()
    commands = {
        "health": "Check /api/health",
        "server start": "Start pnpm dev in background",
        "server stop": "Stop tracked dev server",
        "server status": "Show pid + health",
        "pdf parse <path>": "Parse a PDF through OpenMAIC",
        "classroom generate -r <text> [-p pdf]": "Submit classroom generation",
        "job status <jobId>": "Check a classroom generation job",
        "job watch <jobId>": "Poll a classroom generation job",
        "quit": "Exit",
    }
    while True:
        try:
            line = input(skin.prompt(project_name="openmaic", modified=False))
        except EOFError:
            click.echo()
            skin.print_goodbye()
            return
        cmd = line.strip()
        if not cmd:
            continue
        if cmd in {"quit", "exit"}:
            skin.print_goodbye()
            return
        if cmd == "help":
            skin.help(commands)
            continue
        argv = shlex.split(cmd)
        try:
            cli.main(args=argv, standalone_mode=False, obj=ctx_obj)
        except SystemExit:
            pass
        except Exception as e:
            skin.error(str(e))


@cli.command()
@PASS_CTX
def health(ctx_obj: dict):
    emit(_client(ctx_obj).health(), ctx_obj["as_json"])


@cli.group()
def server():
    pass


@server.command("start")
@PASS_CTX
def server_start(ctx_obj: dict):
    result = _backend(ctx_obj).start_dev()
    emit(result, ctx_obj["as_json"])


@server.command("stop")
@PASS_CTX
def server_stop(ctx_obj: dict):
    result = _backend(ctx_obj).stop()
    emit(result, ctx_obj["as_json"])


@server.command("status")
@PASS_CTX
def server_status(ctx_obj: dict):
    result = _backend(ctx_obj).status()
    emit(result, ctx_obj["as_json"])


@cli.group()
def pdf():
    pass


@pdf.command("parse")
@click.argument("pdf_path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--provider", default="unpdf", show_default=True)
@PASS_CTX
def pdf_parse(ctx_obj: dict, pdf_path: Path, provider: str):
    result = _client(ctx_obj).parse_pdf(pdf_path, provider_id=provider)
    if result.get("success"):
        ctx_obj["session"].update(last_pdf_path=str(pdf_path))
    emit(result, ctx_obj["as_json"])


@cli.group()
def classroom():
    pass


@classroom.command("generate")
@click.option("-r", "--requirement", required=True, help="Requirement text")
@click.option("-l", "--language", default="zh-CN", show_default=True)
@click.option("-p", "--pdf", "pdf_path", type=click.Path(exists=True, dir_okay=False, path_type=Path), default=None)
@PASS_CTX
def classroom_generate(ctx_obj: dict, requirement: str, language: str, pdf_path: Path | None):
    client = _client(ctx_obj)
    pdf_text = None
    pdf_images = None
    if pdf_path is not None:
        parsed = client.parse_pdf(pdf_path)
        if not parsed.get("success"):
            emit(parsed, ctx_obj["as_json"])
            raise SystemExit(1)
        data = parsed.get("data", {})
        pdf_text = data.get("text")
        pdf_images = data.get("images") or []
        ctx_obj["session"].update(last_pdf_path=str(pdf_path))
    result = client.generate_classroom(requirement, language=language, pdf_text=pdf_text, pdf_images=pdf_images)
    if result.get("success"):
        job_id = result.get("jobId") or result.get("data", {}).get("jobId")
        poll_url = result.get("pollUrl") or result.get("data", {}).get("pollUrl")
        ctx_obj["session"].update(last_requirement=requirement, last_job_id=job_id, last_poll_url=poll_url)
    emit(result, ctx_obj["as_json"])


@cli.group()
def job():
    pass


@job.command("status")
@click.argument("job_id")
@PASS_CTX
def job_status(ctx_obj: dict, job_id: str):
    result = _client(ctx_obj).job_status(job_id)
    emit(result, ctx_obj["as_json"])


@job.command("watch")
@click.argument("job_id", required=False)
@click.option("--interval", default=10, show_default=True, type=int)
@click.option("--max-polls", default=30, show_default=True, type=int)
@PASS_CTX
def job_watch(ctx_obj: dict, job_id: str | None, interval: int, max_polls: int):
    state = ctx_obj["session"].load()
    target_job = job_id or state.get("last_job_id")
    if not target_job:
        raise click.ClickException("No job id provided and no previous job tracked.")
    client = _client(ctx_obj)
    last = None
    for _ in range(max_polls):
        result = client.job_status(target_job)
        if ctx_obj["as_json"]:
            click.echo(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            data = result.get("data", result)
            summary = {
                "jobId": data.get("jobId"),
                "status": data.get("status"),
                "step": data.get("step"),
                "progress": data.get("progress"),
                "done": data.get("done"),
            }
            if summary != last:
                emit(summary, False)
                click.echo()
                last = summary
        data = result.get("data", result)
        if data.get("done") or data.get("status") in {"failed", "succeeded"}:
            return
        time.sleep(interval)


@cli.command("session")
@PASS_CTX
def session_cmd(ctx_obj: dict):
    emit(ctx_obj["session"].load(), ctx_obj["as_json"])


def main():
    cli()


if __name__ == "__main__":
    main()
