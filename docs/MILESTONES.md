# Milestones (about 12 weeks at 8 to 12 hours per week)

Stretch each milestone rather than cutting evals if time is short.

## M0: Setup (week 1)
- [x] Monorepo with layout from `REPO_STRUCTURE.md` (package and directory scaffolding)
- [x] `.gitignore` (with `.env`), `.env.example`
- [x] Python tooling: root project, uv lockfile, pytest, Ruff, shared settings
- [ ] Docker Compose: Postgres with pgvector, Redis
- [ ] FastAPI skeleton with `/healthz`
- [ ] GitHub Actions: ruff + pytest on every push
- [ ] Pick the season and list 10 to 15 metrics
Done when: `docker compose up` starts everything and CI is green.

## M1: Data and schema (week 2)
- [ ] Alembic migrations from `DATA_SCHEMA.md` (adjusted to real columns)
- [ ] Idempotent ingestion of play-by-play into `games` and `plays`
- [ ] Data-quality tests (row counts, null checks, key uniqueness)
- [ ] Indexes added, with `EXPLAIN ANALYZE` before/after recorded
- [ ] Table and column descriptions written
Done when: re-running ingestion creates no duplicates and the schema is documented.
Record: rows loaded, ingest time, query times.

## M2: Contextual layer and baseline agent (weeks 3 to 4)
- [ ] `metric_registry` and `schema_descriptions` populated, embedded in pgvector
- [ ] Retrieval of definitions by question
- [ ] Agent loop with SQL tool and chart tool, Pydantic-validated tool calls
- [ ] SQL guardrails (read-only role, allowlist, limits, timeout)
- [ ] 30 golden questions and one-command eval harness
- [ ] Ablation: with vs without registry
Done when: the harness runs in CI and a baseline score is recorded.
Record: accuracy, latency, cost per question, ablation delta.

## M3: ML models (weeks 5 to 6)
- [ ] Features and splits per `ML_PLAN.md` (grouped by game)
- [ ] Win probability: logistic baseline, then LightGBM, tuned with Optuna
- [ ] Calibration (Brier score, reliability curve)
- [ ] Regression model vs rolling-average baseline
- [ ] Anomaly detector
- [ ] Artifacts to S3, ML service endpoints, agent ML tool
Done when: each model beats its baseline on held-out games and results are tabled.
Record: accuracy, Brier, calibration, inference latency.

## M4: RAG module (weeks 7 to 8)
- [ ] One or two document sources, terms checked
- [ ] Chunking comparison (fixed vs structure-aware)
- [ ] Hybrid retrieval (full-text + vector, rank fusion), metadata filters
- [ ] Reranker
- [ ] Cited answers with abstain behavior
- [ ] Router for SQL / RAG / ML / combinations
- [ ] Retrieval eval set (about 40 labeled pairs), prompt-injection test
Done when: recall@k, MRR, faithfulness, and routing accuracy are tracked in CI.
Record: ablation table.

## M5: Production layer (week 9)
- [ ] Redis caching with versioned keys
- [ ] RQ background jobs for ingestion
- [ ] Rate limiting and JWT auth
- [ ] WebSocket replay for live win probability
- [ ] Langfuse tracing and structured logs
- [ ] k6 load test
Done when: before/after p50/p95 latency and cache hit rate are recorded.

## M6: Web app (week 10)
- [ ] Chat with streaming answers and citations
- [ ] Win-probability chart with anomaly markers
- [ ] Dashboard for eval and model results
Done when: a new user can ask a question and get a cited answer from the UI alone.

## M7: Deploy and CI/CD (week 11)
- [ ] Dockerfiles for every service
- [ ] CI gate: tests + evals, fail on regression
- [ ] Deploy to AWS (see `INFRA_AND_CICD.md`)
- [ ] Live URL
Done when: a merge to main runs tests and evals and deploys.

## M8: Polish (week 12)
- [ ] README with architecture diagram
- [ ] Design-decisions section (from `DECISIONS.md`)
- [ ] 2 to 3 minute demo video
- [ ] Results table and resume bullets from measured numbers

## If behind, cut in this order
1. Roster planner and multimodal (already stretch)
2. Terraform
3. Reranker (keep hybrid search)
4. Anomaly detector (keep win probability and one regression)
Never cut: eval harness, contextual-layer ablation, load test.
