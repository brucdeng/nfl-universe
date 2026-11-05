# nfl-universe

An NFL analytics application combining a tool-using LLM agent, document retrieval,
and ML models over one completed season. See `docs/PROJECT_OVERVIEW.md` for scope.

## Current status
M0 steps 1-5 are implemented: repository scaffolding, Python tooling, shared
settings, a Compose stack, FastAPI health endpoints, and a GitHub Actions workflow.
Live container integration and the first hosted CI run still need verification.
The season and initial metrics are the remaining M0 scope decisions. The frontend
and agent/RAG/ML algorithms are placeholders.

## Run the local stack
Install and start Docker Desktop with Linux containers (WSL 2 on Windows).
From the repository root:

```powershell
docker compose up --build
```

Compose starts Postgres 17 with pgvector installed, Redis, and the API. It works
with local development defaults even without a `.env` file. The API waits for
healthy database/cache containers and reloads changes under `api/app` and
`shared/shared`. Host ports are bound to loopback only.

- Health: http://localhost:8000/healthz
- Process liveness: http://localhost:8000/livez
- API documentation: http://localhost:8000/docs

`/healthz` returns HTTP 200 with
`{"status":"ok","checks":{"postgres":"ok","pgvector":"ok","redis":"ok"}}`.
It returns HTTP 503 if a check fails. `/livez` stays independent of dependencies.
The pgvector check verifies the extension is available for installation; M1's
Alembic migrations will enable it and create application tables.

```powershell
docker compose ps
docker compose logs api
docker compose down
```

Named volumes retain Postgres and Redis data when the stack stops. Role bootstrap
runs only on a new Postgres volume: it creates separate non-superuser `app_rw` and
`agent_ro` accounts, with the latter defaulting to read-only transactions. Table
grants will be restricted to the agent allowlist in M1. Changing `.env` passwords
does not change roles in an existing database.

`.env.example` documents local credentials and optional port overrides. These
defaults are for local development only. Compose supplies container hostnames
directly; the `DATABASE_URL` and `REDIS_URL` examples use localhost for running
Python on the host. If you change passwords or published ports, update those host
URLs too. On a machine with working Python database drivers, start just the
dependencies with `docker compose up -d postgres redis`, then run
`python -m uv run uvicorn app.main:app --reload` after configuring `.env`.

## Local Python setup
Run from the repository root. Development uses Python 3.12 (`.python-version`);
the project declares Python 3.11+ support, but this setup was verified on 3.12.

```powershell
python -m pip install --user uv
python -m uv sync --locked
# On first setup only; preserve .env if it already exists:
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
python -m uv run pytest
python -m uv run ruff check .
python -m uv run ruff format --check .
```

If `uv` is on PATH, `uv` and `python -m uv` are interchangeable. Dependencies are
installed into the ignored `.venv`; commit `uv.lock` for reproducible installs.
There is no need to activate the virtual environment when using `uv run`.

`shared/shared/settings.py` loads environment variables and the working directory's
`.env`; environment variables take precedence. Blank integration settings are
unset. Unit tests need no database, cloud credentials, or model downloads.
The API validates `DATABASE_URL` and `REDIS_URL` at startup. Never
use the write-role database connection as a fallback for the agent's read-only role.

## Tests and CI
`python -m uv run pytest` runs the local unit suite and skips integration tests
unless explicit test URLs are supplied. With the Compose stack running and the
default local credentials:

```powershell
$env:TEST_DATABASE_URL = "postgresql+psycopg://app_rw:local-app-password@localhost:5432/nfl_universe"
$env:TEST_REDIS_URL = "redis://localhost:6379/0"
$env:TEST_API_URL = "http://localhost:8000"
python -m uv run pytest -m integration
```

Use dedicated test services, not a production database. The integration suite checks
real connections, pgvector availability, bootstrap role properties, and health
responses from both the app and the running API container.

`.github/workflows/ci.yml` runs on pushes and pull requests, with manual dispatch
available. It runs Ruff and unit tests on Python 3.11/3.12, then builds and starts
the Compose stack in a separate job for integration checks. It prints container
logs on failure and removes the disposable CI stack afterward. No repository
secrets are needed for this M0 workflow. Frontend checks and eval gates will be
added when those components exist.

Verification on 2026-11-05: unit tests, Ruff, Compose configuration validation,
and workflow lint passed. Docker Engine/Desktop was unavailable locally, so the
live stack tests remain unverified here. Windows Application Control also blocked
the native psycopg binary; the intended API runtime is the Linux container.

## How to use
1. Read `AGENTS.md` for collaboration rules (guided mode by default).
2. Read `docs/PROJECT_OVERVIEW.md`, then `docs/ARCHITECTURE.md`.
3. Start each session with the matching prompt from `docs/SESSION_PROMPTS.md`.
4. Update `docs/RESULTS_LOG.md` and `docs/DECISIONS.md` as you go. They become your resume bullets and interview notes.

## Files
| File | Purpose |
|---|---|
| `AGENTS.md` | Root instructions: stack, rules, collaboration mode |
| `docs/PROJECT_OVERVIEW.md` | Goals, scope, skills mapping |
| `docs/ARCHITECTURE.md` | Components, diagram, request flows, trade-offs |
| `docs/MILESTONES.md` | M0 to M8 with checklists and done criteria |
| `docs/REPO_STRUCTURE.md` | Monorepo layout |
| `docs/DATA_SCHEMA.md` | Draft Postgres schema and indexes |
| `docs/METRIC_REGISTRY.md` | Contextual-layer format and starter metrics |
| `docs/AGENT_DESIGN.md` | Agent loop, tools, guardrails, output schema |
| `docs/RAG_DESIGN.md` | Retrieval pipeline and experiments |
| `docs/ML_PLAN.md` | Models, features, validation, tuning |
| `docs/EVALUATION.md` | Eval suites, golden questions, CI gate |
| `docs/API_SPEC.md` | Draft HTTP and WebSocket endpoints |
| `docs/INFRA_AND_CICD.md` | Docker, CI, AWS, load testing, observability |
| `docs/CODING_STANDARDS.md` | Conventions for Python, TypeScript, SQL, tests |
| `docs/SESSION_PROMPTS.md` | Ready-to-paste prompts per milestone |
| `docs/RESULTS_LOG.md` | Measurement tables and resume bullet templates |
| `docs/DECISIONS.md` | Architecture decision log |

Anything marked "verify" or "TBD" is an open item. Check it against the real data, library, or terms of use before relying on it.
