# OPENMAIC.md

Project-specific CLI-Anything analysis for OpenMAIC.

## Target software

- **Software:** OpenMAIC
- **Source path:** `/Users/rich/.openclaw/workspace/OpenMAIC`
- **Backend model:** local Next.js service plus OpenMAIC HTTP APIs
- **Hard dependency:** a working OpenMAIC checkout with Node/pnpm and the OpenMAIC server itself

## Why a CLI layer makes sense

OpenMAIC is primarily a browser application, but the useful control surface for an agent already exists behind HTTP endpoints:

- `GET /api/health`
- `POST /api/parse-pdf`
- `POST /api/generate-classroom`
- `GET /api/generate-classroom/{jobId}`

That means the CLI should wrap the **real OpenMAIC server** rather than trying to reimplement classroom generation logic.

## Backend mapping

### GUI / user action → CLI / backend

- Start local app → `server start` → `pnpm dev`
- Stop local app → `server stop`
- Check whether app is healthy → `health`
- Upload PDF in UI → `pdf parse <file>` → `POST /api/parse-pdf`
- Click generate classroom → `classroom generate` → `POST /api/generate-classroom`
- Watch job progress in UI → `job status <jobId>` / `job watch <jobId>`

## State model

State is stored in a JSON session file under `~/.cli-anything-openmaic/session.json` and tracks:

- `repo_dir`
- `base_url`
- `pid_file`
- `last_job_id`
- `last_poll_url`
- `last_pdf_path`
- `last_requirement`

This lets REPL mode keep context between commands without retyping flags.

## First harness scope

The first useful CLI layer focuses on operations that are already stable and externally exposed:

1. Server lifecycle
2. Health checks
3. PDF parsing
4. Classroom job submission
5. Job status / watch
6. JSON output for agent consumption
7. REPL default path

## Known limitations

- Successful classroom generation still depends on OpenMAIC server-side provider configuration.
- The CLI does not bypass API-key or model configuration.
- It intentionally wraps existing APIs instead of exposing internal generation primitives directly.
