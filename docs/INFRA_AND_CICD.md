# Infra and CI/CD

## Local (Docker Compose)
Implemented in M0: `postgres` (pgvector 0.8.7 / Postgres 17), `redis` (7.4), and
`api` (Python 3.12). `docker compose up --build` starts them with health checks,
named data volumes, loopback host ports, and API/shared source mounts for reload.
The API runs as a non-root user and connects as `app_rw`. Database bootstrap
creates non-superuser `app_rw` and `agent_ro` roles; application schema, extension
activation, and table grants arrive through Alembic in M1. The API container
does not receive administrator or agent database credentials.

Planned services: `agent`, `rag`, `ml`, `worker` (RQ), `web`, optional `langfuse`.
A `make up` convenience target is still planned; direct Compose commands work on
Windows without Make. See README for startup and integration-test instructions.

## Environment variables (keep `.env.example` current)
`DATABASE_URL`, `DATABASE_URL_READONLY`, `REDIS_URL`, `S3_BUCKET`, `AWS_REGION`, `LLM_API_KEY`, `LLM_MODEL`, `EMBEDDING_MODEL`, `RERANKER_MODEL`, `JWT_SECRET`, `LANGFUSE_*`, `DATA_VERSION`.
Compose also accepts `POSTGRES_PASSWORD`, `APP_DB_PASSWORD`, `AGENT_DB_PASSWORD`,
`POSTGRES_PORT`, `REDIS_PORT`, and `API_PORT`. Example passwords are local-only
defaults. Use URL-safe password characters with the current Compose URL template.
Never commit real credentials. Use a secrets manager or CI secrets in deployment.

## GitHub Actions
Implemented `ci.yml` runs on every push, PR, and manual dispatch. The `checks` job
installs the lockfile, runs Ruff lint/format checks, and runs unit tests on Python
3.11 and 3.12. The `stack` job validates Compose, builds the API image, waits for
healthy services, and runs integration tests against the real services and HTTP
endpoint. It emits logs on failure and always cleans up its disposable volumes.
Actions are pinned to commit SHAs; uv is pinned to 0.13.7. No cloud/LLM secrets are
needed. The first hosted run is pending a push of this workflow.

Target workflow as later milestones arrive:
1. Install with uv, cache dependencies.
2. ruff check and format check.
3. pytest (unit and integration against service containers for Postgres and Redis).
4. Frontend: install, typecheck, lint, test, build.
5. Fast eval subset with the regression gate (see `EVALUATION.md`).
6. Docker build for each service.

`deploy.yml` on merge to main: build and push images, deploy, run a smoke test against the live URL.

## AWS (keep it simple first)
- Start: one EC2 instance running Docker Compose, S3 for artifacts. Consider RDS for Postgres if you want a managed database story.
- Stretch: ECS services, and Terraform for repeatability.
- Security: least-privilege IAM role for S3 access, security groups restricting Postgres and Redis to internal traffic, HTTPS in front.
- Record monthly cost estimate in `DECISIONS.md`.

## Load testing (k6)
Scripts in `infra/k6/`. Scenarios:
- Repeated agent questions (cache cold, then warm)
- Win-probability endpoint under concurrent users
- WebSocket replay with N concurrent clients
Record for each: concurrent users, p50/p95/p99 latency, error rate, throughput, cache hit rate. Run before and after each optimization.

## Observability
- Structured JSON logs with request id and trace id.
- Prometheus-style metrics endpoint (request counts, latency histograms, cache hits, queue depth).
- Langfuse traces for agent runs (cost, tokens, tool calls).
- Alert-worthy signals to document: error rate, p95 latency, queue backlog, eval score drop.

## Backups and data
- Raw data snapshots in S3 with versioning.
- Migrations via Alembic only. Never edit the database by hand in deployed environments.
