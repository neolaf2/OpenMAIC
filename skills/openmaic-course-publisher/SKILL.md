---
name: openmaic-course-publisher
description: This skill should be used when the user wants to generate arbitrary course modules with local OpenMAIC, turn requirements or PDFs into a classroom, track the generation job, and return the resulting localhost classroom webpage for presentation on the local machine.
user-invocable: true
metadata: { "openclaw": { "emoji": "🏫" } }
---

# OpenMAIC Course Publisher

Use this skill to generate and publish local OpenMAIC classrooms through the `cli-anything-openmaic` harness.

Prefer this skill over the base `openmaic` setup skill once OpenMAIC and the harness already exist locally and the user is asking for actual course/module generation.

## Trigger conditions

Use this skill when the user asks to:

- create a course module with OpenMAIC
- turn requirements into a lesson/classroom
- turn a PDF or outline into a lesson/classroom
- publish or host the generated classroom locally
- get a local webpage URL for an OpenMAIC classroom
- generate reusable teaching modules on demand

## Core operating rules

- Treat the local OpenMAIC classroom URL as the published local webpage unless the user explicitly asks for a separate export format.
- Use the real local OpenMAIC service rather than reimplementing generation logic.
- Use the wrapper script at `scripts/openmaic_course.sh` for all CLI calls.
- Check health before generation.
- If the user attached a local PDF, confirm before reading it.
- Once the user clearly asks to generate a module/classroom, do not ask for a second confirmation before submission.
- Do not resubmit a job that is already queued or running.
- Return raw local URLs on their own line.
- If generation fails because of provider configuration, direct the user to the OpenMAIC server-side config instead of inventing request-time overrides.

## Local paths

Assume these defaults unless the user says otherwise:

- OpenMAIC repo: `/Users/rich/.openclaw/workspace/OpenMAIC`
- Harness venv CLI: `/Users/rich/.openclaw/workspace/OpenMAIC/agent-harness/.venv/bin/cli-anything-openmaic`
- Wrapper script: `scripts/openmaic_course.sh`

## Workflow

### 1. Verify service readiness

Load `references/workflows.md` and run the health check through the wrapper script.

If the service is unhealthy, start it or inspect status before attempting generation.

### 2. Shape the generation brief

If the user gives only a rough topic, expand it into a concrete requirement brief.

Include as many of these as are available:

- topic
- audience
- language
- learning goals
- scene types such as slides, quizzes, interactive scenes, or PBL
- tone and depth

Load `references/examples.md` when examples help.

### 3. Submit generation

For requirement-only generation, call the wrapper script with `classroom generate`.

For PDF-backed generation, confirm before reading the file, then call the same wrapper with `-p <pdf>`.

### 4. Track the job

Poll the same job id conservatively until it succeeds or fails.

If the turn must end first, return the job id and say the same job can be checked later without resubmitting.

### 5. Publish the result

When the job succeeds, return:

- classroom id
- raw localhost classroom URL on its own line

Treat that URL as the local user-facing webpage.

## Response style

Keep responses operational and concrete.

On success, prefer this format:

```text
Classroom ID: abc123
Local page:
http://localhost:3000/classroom/abc123
```
