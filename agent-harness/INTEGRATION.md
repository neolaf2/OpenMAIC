# OpenMAIC CLI Integration

This fork includes a repo-local wrapper for the `cli-anything-openmaic` harness so the CLI feels like part of the OpenMAIC installation.

## Install the harness into the repo

From the OpenMAIC root:

```bash
pnpm run cli:install
```

This creates the harness virtualenv under:

```text
agent-harness/.venv
```

## Use the repo-local wrapper

The wrapper lives at:

```text
scripts/openmaic-cli
```

It automatically targets the current fork checkout as the repo.

Examples:

```bash
pnpm run cli:health
pnpm run cli:server:status
pnpm run cli:server:start
pnpm run cli -- --json pdf parse /absolute/path/to/file.pdf
pnpm run cli -- --json classroom generate -r "Generate a Chinese module on linear algebra" -l zh-CN
pnpm run cli -- --json job status <jobId>
```

## Why this layout

- keeps the CLI versioned with your fork
- keeps the harness install local to the repo
- avoids polluting global Python
- makes the CLI callable through standard project scripts
