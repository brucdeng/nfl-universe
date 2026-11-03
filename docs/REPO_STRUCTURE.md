# Repo structure

This is the target layout. M0 steps 1-3 create package boundaries, settings, tests,
and placeholder directories; application modules and infrastructure files shown
below are added in their respective milestones.

```
nfl-universe/
  AGENTS.md
  README.md
  docker-compose.yml
  Makefile
  pyproject.toml          # single Python project; Hatchling maps service packages
  uv.lock                 # shared dependency lockfile
  .python-version         # development interpreter: Python 3.12
  .env.example
  .github/workflows/
    ci.yml                # lint, tests, evals, build
    deploy.yml
  docs/                   # this docs pack
  web/                    # React + TypeScript (Vite)
    src/
  api/                    # FastAPI gateway
    app/
      main.py
      routers/
      auth/
      cache/
      deps.py
    tests/
  agent/
    agent/
      loop.py             # planner/executor
      router.py
      tools/              # sql.py, chart.py, rag.py, ml.py
      guardrails.py
      prompts/            # versioned prompt files
      schemas.py          # Pydantic tool and answer schemas
      tracing.py
    tests/
  rag/
    rag/
      ingest.py
      chunking.py
      embed.py
      retrieve.py         # hybrid search + rank fusion
      rerank.py
      cite.py
    tests/
  ml/
    ml/
      features.py
      train_winprob.py
      train_regression.py
      anomaly.py
      calibrate.py
      registry.py         # S3 save/load
      serve.py
    notebooks/            # exploration only, not source of truth
    tests/
  ingest/
    ingest/
      nfl_pbp.py
      docs_sources.py
      jobs.py             # RQ tasks
    tests/
  evals/
    golden/               # *.jsonl question sets
    retrieval/            # labeled query-to-doc pairs
    run_evals.py
    report.py
  infra/
    docker/               # Dockerfiles
    k6/                   # load test scripts
    aws/                  # deploy notes or IaC
  migrations/             # Alembic
  shared/
    shared/
      __init__.py
      settings.py         # centralized environment configuration
    tests/
      test_settings.py
```

Each Python service package has its own `tests/`. One root `pyproject.toml` builds
the importable packages `app`, `agent`, `rag`, `ml`, `ingest`, and `shared` from
their service folders. Shared settings live in `shared/shared/`; future common
Pydantic schemas and DB models belong there too. Services may import `shared`,
but `shared` must not import service packages. See ADR-008 in `DECISIONS.md`.
