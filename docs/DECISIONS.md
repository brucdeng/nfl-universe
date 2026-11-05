# Decision log

Format: date, decision, options considered, why, trade-offs, revisit trigger. Add an entry for any non-obvious choice. These become interview talking points.

## ADR-001: Monorepo with multiple services
- Decision: one repo, services in separate folders.
- Why: shared schemas, one CI, easier to demo.
- Trade-off: needs discipline around package boundaries.
- Shared package layout: resolved in ADR-008 (see `REPO_STRUCTURE.md`).

## ADR-002: Postgres with pgvector instead of a separate vector database
- Why: one system to operate, joins between vectors and relational data.
- Trade-off: lower ceiling on vector-search scale.
- Revisit if: chunk count or latency outgrows pgvector.

## ADR-003: Hybrid retrieval with reciprocal rank fusion
- Why: keyword search catches names and exact terms that embeddings miss.
- Trade-off: more complexity, two indexes to maintain.
- Validate with: the retrieval ablation.

## ADR-004: RQ for background jobs instead of Celery
- Why: simpler with Redis already in the stack.
- Trade-off: fewer features.
- Revisit if: you need complex workflows or scheduling.

## ADR-005: Grouped cross-validation by game
- Why: plays within a game are correlated, so random splits leak.
- Trade-off: fewer independent samples with one season.

## ADR-006: Provider-agnostic LLM wrapper
- Why: swap models for cost/accuracy ablations and avoid lock-in.
- Trade-off: a thin abstraction to maintain.

## ADR-007: One season for v1
- Why: finish the full loop before adding data volume.
- Revisit after: M4 is complete.

## ADR-008: Single Python project with explicit service packages
- Date: 2026-11-03
- Decision: one root `pyproject.toml`, one `uv.lock`, and one local `.venv`.
  Hatchling builds `app`, `agent`, `rag`, `ml`, `ingest`, and `shared` from their
  existing service directories. `shared/shared/` owns settings and future shared
  schemas/models; it must not import service packages.
- Options considered: a uv workspace with separately packaged services; a single
  root project with explicit package mappings.
- Why: simple installation and testing during v1, while preserving code boundaries.
- Trade-offs: dependency resolution and the installed distribution are shared;
  independently deployed services may eventually need smaller dependency sets.
- Revisit if: dependency conflicts or deployment size justify separate packages.
- Build dependency: Hatchling (`>=1.27,<2`) provides explicit wheel package mapping.
- Reference: https://hatch.pypa.io/latest/config/build/

## ADR-009: M0 development tooling and typed settings
- Date: 2026-11-03
- Decision: Python 3.12 for local development, with package compatibility declared
  as Python 3.11+. Use uv for environment management and the committed lockfile.
  Add Pydantic v2 and pydantic-settings v2 for centralized typed settings, and
  pytest and Ruff in the development dependency group. Exact resolved runtime and
  development versions live in `uv.lock`.
- Options considered: manual environment parsing versus pydantic-settings; installing
  the entire planned stack now versus adding dependencies as integrations arrive.
- Why: typed configuration catches invalid values, and M0 checks need no external
  services. Environment variables override a UTF-8 `.env` in the working directory.
- Trade-offs: unused integration settings remain optional for now; each future
  service must validate its own required configuration at startup. Local checks
  currently verify Python 3.12 only.
- Secret values use `SecretStr` to redact ordinary repr/JSON output. The read-only
  database setting is independent and never defaults to the write-role connection.
- Ruff checks errors, imports, modernization, and common bug patterns. Pytest uses
  importlib mode so similarly named service test files can coexist.
- Revisit if: a dependency requires a higher Python minimum or service-specific
  settings become necessary.
- References: https://docs.astral.sh/uv/concepts/projects/config/ and
  https://docs.pydantic.dev/latest/concepts/pydantic_settings/

## ADR-010: M0 API health checks and connection clients
- Date: 2026-11-05
- Decision: add FastAPI and Uvicorn for the gateway, SQLAlchemy 2.0 with Psycopg 3
  binary distribution for Postgres, and redis-py for Redis. Add HTTPX2 as a dev
  dependency for the installed Starlette TestClient and HTTP integration tests.
  The resolved versions and dependency bounds live in `uv.lock` and `pyproject.toml`.
- Options considered: synchronous clients in FastAPI's thread pool versus async
  database/cache clients; a combined health endpoint versus separate liveness.
- Why: a small synchronous health route is sufficient for setup. `/healthz` checks
  a real query, pgvector availability, and Redis PING; `/livez` checks only the
  process. Lifespan owns connection creation/cleanup. Missing required settings
  fail startup, while unavailable dependencies produce HTTP 503 and can recover.
- Trade-offs: checks run sequentially, with bounded connection, pool, statement,
  and socket waits. Redis automatic retries are disabled. Revisit client strategy
  as streaming and load tests are introduced.
- Configuration errors and health responses avoid exposing connection details.
  The gateway uses only its write-role URL; the agent keeps its own read-only URL.
- Local limitation: Windows Application Control blocked the Psycopg native binary
  on this development machine. Do not change OS protections; use the Linux API
  container for runtime. Unit tests isolate service clients, while CI tests the
  real Linux driver and connections.
- References: https://fastapi.tiangolo.com/advanced/events/,
  https://docs.sqlalchemy.org/en/20/dialects/postgresql.html,
  https://redis.readthedocs.io/en/stable/retry.html

## ADR-011: Local Compose bootstrap and M0 CI
- Date: 2026-11-05
- Decision: use pgvector 0.8.7 on Postgres 17, Redis 7.4, and Python 3.12 for the
  initial Compose stack. Use health-based startup dependencies, loopback host
  ports, named data volumes, and source mounts for API development. The API image
  installs locked runtime dependencies and runs as a non-root user.
- Options considered: Postgres superuser credentials for the API versus dedicated
  roles; CI service containers versus testing the same Compose stack as local dev.
- Why: separate `app_rw` and `agent_ro` roles establish the intended privilege
  boundaries, and Compose-based CI exercises the actual image and startup wiring.
- Bootstrap only provisions cluster roles and basic connection/schema usage
  permissions on the initial data volume. `agent_ro` defaults to read-only
  transactions and cannot create databases, roles, or public-schema objects.
  M1 migrations will enable pgvector and add tables plus explicit allowlist grants.
- Trade-offs: image tags pin the main versions but are not immutable digests;
  initial development passwords are public local defaults, and changing an env
  password does not update existing database roles. Production configuration is
  a separate deployment task. Docker is required for full integration tests.
- CI: Ruff and unit tests on Python 3.11/3.12; a separate Linux stack job builds
  and checks the API, Postgres, and Redis. Use read-only workflow permissions,
  SHA-pinned actions, uv 0.13.7, failure logs, and unconditional CI cleanup.
- Revisit if: deployment requirements call for immutable image digests, managed
  services, separate dependency groups, or a dedicated development override file.
- References: https://github.com/pgvector/pgvector#docker,
  https://docs.docker.com/compose/how-tos/startup-order/,
  https://github.com/astral-sh/setup-uv

## Template
```
## ADR-00X: Title
- Date:
- Decision:
- Options considered:
- Why:
- Trade-offs:
- Revisit if:
```
