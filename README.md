# nfl-universe

An NFL analytics application combining a tool-using LLM agent, document retrieval,
and ML models over one completed season. See `docs/PROJECT_OVERVIEW.md` for scope.

## Current status
M0 steps 1-3 are implemented: Git, service/package scaffolding, Python tooling, and
shared settings. Docker Compose, the FastAPI application, and GitHub Actions are
the next setup tasks. The frontend and agent/RAG/ML algorithms are placeholders.

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
unset. No database, cloud credentials, or model downloads are needed for these
checks. Services will validate their required settings when implemented. Never
use the write-role database connection as a fallback for the agent's read-only role.

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
