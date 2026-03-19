# TEST.md

## Test Inventory Plan

- `test_core.py`: 5 unit tests planned
- `test_full_e2e.py`: 4 E2E tests planned

## Unit Test Plan

### `core/session.py`
- verify default session structure
- verify update persists values
- expected test count: 2

### `core/project.py`
- verify repo detection succeeds on a valid OpenMAIC tree
- verify repo detection fails on an invalid path
- expected test count: 2

### `core/api.py`
- verify classroom payload structure includes nested `pdfContent`
- expected test count: 1

## E2E Test Plan

### Workflow 1: health check against real backend
- Simulates: agent verifying OpenMAIC availability
- Operations chained: call installed CLI `health`
- Verified: JSON response indicates server health endpoint is reachable

### Workflow 2: parse a real PDF through backend
- Simulates: user supplying source material for course generation
- Operations chained: call installed CLI `pdf parse <file> --json`
- Verified: parsed text returned, success true

### Workflow 3: submit a classroom generation job
- Simulates: user triggering classroom creation with PDF-backed context
- Operations chained: parse PDF, submit generation request
- Verified: job id returned or backend failure surfaced as structured JSON

### Workflow 4: session + status roundtrip
- Simulates: agent resuming prior context
- Operations chained: inspect stored session, check server status
- Verified: repo path and URL persist; status output is structured

## Realistic Workflow Scenarios

### Workflow name: PDF-backed course generation kickoff
- Simulates: creating a classroom from a user-uploaded outline PDF
- Operations chained:
  1. verify health
  2. parse source PDF
  3. submit classroom generation request
  4. inspect returned job id
- Verified:
  - health endpoint responds
  - parser extracts non-empty text
  - generation request returns structured JSON

---

## Test Results

```text
============================= test session starts ==============================
platform darwin -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0 -- /Users/rich/.openclaw/workspace/OpenMAIC/agent-harness/.venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/rich/.openclaw/workspace/OpenMAIC/agent-harness
collecting ... [_resolve_cli] Using installed command: /Users/rich/.openclaw/workspace/OpenMAIC/agent-harness/.venv/bin/cli-anything-openmaic
collected 9 items

cli_anything/openmaic/tests/test_core.py::test_session_defaults PASSED
cli_anything/openmaic/tests/test_core.py::test_session_update_persists PASSED
cli_anything/openmaic/tests/test_core.py::test_ensure_repo_dir_accepts_valid_repo PASSED
cli_anything/openmaic/tests/test_core.py::test_ensure_repo_dir_rejects_invalid_repo PASSED
cli_anything/openmaic/tests/test_core.py::test_generate_classroom_uses_nested_pdf_content PASSED
cli_anything/openmaic/tests/test_full_e2e.py::TestCLISubprocess::test_help PASSED
cli_anything/openmaic/tests/test_full_e2e.py::TestCLISubprocess::test_health_json PASSED
cli_anything/openmaic/tests/test_full_e2e.py::TestCLISubprocess::test_pdf_parse_json 
  Parsed PDF: /Users/rich/.openclaw/media/inbound/Ai_x-key-method---199944db-971d-46af-985b-5c034973ef6b.pdf (2851 chars)
PASSED
cli_anything/openmaic/tests/test_full_e2e.py::TestCLISubprocess::test_classroom_generate_submission_json 
  Classroom job: VBz2x75Y1S
PASSED

============================== 9 passed in 0.46s ===============================
```

## Summary Statistics

- Total tests: 9
- Passed: 9
- Pass rate: 100%
- Execution time: 0.46s

## Coverage Notes

- Covers session persistence, repo detection, nested classroom payload shape, installed CLI help/JSON behavior, real `/api/health`, real PDF parsing, and real classroom job submission.
- The harness intentionally wraps the real OpenMAIC server APIs rather than internal generation primitives.
- Full classroom completion is not asserted in tests because end-to-end generation depends on external provider configuration and long-running model execution; the tested contract is successful submission plus structured job tracking.
