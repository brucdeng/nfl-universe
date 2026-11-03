# Infra and CI/CD

## Local (Docker Compose)
Services: `postgres` (pgvector image), `redis`, `api`, `agent`, `rag`, `ml`, `worker` (RQ), `web`, optional `langfuse`. Mount code for dev. Health checks on every service. One `make up` target.

## Environment variables (keep `.env.example` current)
`DATABASE_URL`, `DATABASE_URL_READONLY`, `REDIS_URL`, `S3_BUCKET`, `AWS_REGION`, `LLM_API_KEY`, `LLM_MODEL`, `EMBEDDING_MODEL`, `RERANKER_MODEL`, `JWT_SECRET`, `LANGFUSE_*`, `DATA_VERSION`.
Never commit real values. Use a secrets manager or CI secrets in deployment.

## GitHub Actions
`ci.yml` on every PR:
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
