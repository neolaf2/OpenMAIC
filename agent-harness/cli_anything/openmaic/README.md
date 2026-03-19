# cli-anything-openmaic

CLI-Anything harness for OpenMAIC.

## What it wraps

This harness talks to the **real OpenMAIC server** and uses the real local repo for lifecycle commands.

Current command surface:

- `health`
- `server start`
- `server stop`
- `server status`
- `pdf parse <file>`
- `classroom generate --requirement ... [--pdf file]`
- `job status <jobId>`
- `job watch <jobId>`
- `session`

## Hard dependencies

- OpenMAIC repository checkout
- Node.js and `pnpm`
- A runnable OpenMAIC installation
- Provider keys in `.env.local` or `server-providers.yml` for successful classroom generation

## Install the CLI

From `agent-harness/`:

```bash
pip install -e .
```

## Basic usage

Run inside the OpenMAIC repo, or pass `--repo` explicitly.

```bash
cli-anything-openmaic --repo /path/to/OpenMAIC health
cli-anything-openmaic --repo /path/to/OpenMAIC server start
cli-anything-openmaic --repo /path/to/OpenMAIC pdf parse ./deck.pdf --json
cli-anything-openmaic --repo /path/to/OpenMAIC classroom generate -r "Teach me quantum mechanics" -l en-US
cli-anything-openmaic --repo /path/to/OpenMAIC job watch JDPUmHGy0V
```

Invoke without a subcommand to enter the REPL:

```bash
cli-anything-openmaic --repo /path/to/OpenMAIC
```

## JSON mode

Add `--json` before the subcommand:

```bash
cli-anything-openmaic --repo /path/to/OpenMAIC --json health
```

## Notes

- `classroom generate --pdf file.pdf` first calls `/api/parse-pdf`, then submits `/api/generate-classroom`.
- Session state is stored in `~/.cli-anything-openmaic/session.json`.
- `server start` tracks the background `pnpm dev` PID in `~/.cli-anything-openmaic/openmaic-dev.pid`.
