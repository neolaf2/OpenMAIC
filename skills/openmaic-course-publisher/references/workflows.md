# OpenMAIC Course Publisher Workflows

## Core idea

This skill sits **on top of** the local `cli-anything-openmaic` harness and uses the real local OpenMAIC server.

Treat the generated classroom URL as the local user-facing webpage unless the user explicitly asks for a separate export pipeline.

## Preconditions

Check these before generation:

1. OpenMAIC repo exists at `/Users/rich/.openclaw/workspace/OpenMAIC` unless the user says otherwise.
2. CLI wrapper exists at `skills/openmaic-course-publisher/scripts/openmaic_course.sh`.
3. Harness CLI exists at `/Users/rich/.openclaw/workspace/OpenMAIC/agent-harness/.venv/bin/cli-anything-openmaic`.
4. OpenMAIC server is healthy.

Health check command:

```bash
skills/openmaic-course-publisher/scripts/openmaic_course.sh --json health
```

If health fails, start or restart the OpenMAIC server first:

```bash
skills/openmaic-course-publisher/scripts/openmaic_course.sh --json server status
skills/openmaic-course-publisher/scripts/openmaic_course.sh --json server start
```

## Requirement-only generation

Use when the user gives a topic, audience, or desired module structure without a source file.

Command pattern:

```bash
skills/openmaic-course-publisher/scripts/openmaic_course.sh --json classroom generate -r "<requirement>" -l zh-CN
```

## PDF-backed generation

Use when the user attaches a PDF or explicitly wants a module built from an existing deck/outline.

Command pattern:

```bash
skills/openmaic-course-publisher/scripts/openmaic_course.sh --json classroom generate -r "<requirement>" -p /absolute/path/to/file.pdf -l zh-CN
```

This internally parses the PDF and submits the generation job.

## Polling / publication

Once a job is submitted, track it via:

```bash
skills/openmaic-course-publisher/scripts/openmaic_course.sh --json job status <jobId>
```

When the response contains:

- `data.status = succeeded`
- `data.result.classroomId`
- `data.result.url`

return that `data.result.url` as the local user-facing webpage.

That URL is typically:

```text
http://localhost:3000/classroom/<classroomId>
```

## Response contract

When generation succeeds, return:

- classroom id
- raw local classroom URL on its own line
- one-sentence explanation that this is the locally served webpage

Example:

```text
Classroom ID: abc123
Local page:
http://localhost:3000/classroom/abc123
```

## Failure handling

- If health fails, say the local OpenMAIC server is not healthy and start or inspect it.
- If submission fails with provider/model/auth errors, direct the user to `.env.local` or `server-providers.yml`.
- If the job is still `queued` or `running`, do not resubmit; keep polling the same job.
