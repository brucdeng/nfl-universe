# Results log

Record every measurement here with the date, git SHA, and config. Only write numbers you measured. Resume bullets are drafted from this file.

## M0 local stack verification
| Date | Git SHA | Configuration | Result |
|---|---|---|---|
| 2026-11-05 | eee6485 | Docker Desktop Engine 29.9.2, Compose 5.6.1, Linux containers; checked-in Compose defaults; Python 3.12.16, pytest 9.2.0 | API, Postgres, and Redis healthy; full suite: 20 passed, 0 skipped (including 3 integration tests); host `/healthz` and `/livez` returned success |

Built with `docker compose up --build --detach --wait --wait-timeout 180`.
Tests used the temporary Linux test-container command in README with the repository
mounted read-only and the checked-in lockfile. The API used its real `app_rw`
connection; checks verified pgvector availability, separate database roles, Redis
PING, and the running API HTTP endpoints. This is local verification, not a hosted
GitHub Actions result or a load-test benchmark.

## Data and database
| Date | Change | Rows | Ingest time | Query | Before (ms) | After (ms) |
|---|---|---|---|---|---|---|
| | | | | | | |

## Agent evals
| Date | Git SHA | Prompt version | Model | Contextual layer | Questions | Accuracy | Median latency | Cost per question |
|---|---|---|---|---|---|---|---|---|
| | | | | none | | | | |
| | | | | schema only | | | | |
| | | | | schema + registry | | | | |

## Retrieval and RAG
| Date | Chunking | Retrieval | Reranker | k | recall@k | MRR | Faithfulness | Citation accuracy | Latency |
|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | |

## Routing
| Date | Questions | Routing accuracy | Notes |
|---|---|---|---|
| | | | |

## ML models
| Date | Model | CV scheme | Accuracy | Log loss | Brier | MAE/RMSE | vs baseline | Inference p50/p95 |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |

## Load tests
| Date | Scenario | Cache | Concurrent users | p50 | p95 | p99 | Error rate | Throughput | Hit rate |
|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | |

## Resume bullet templates (fill only with measured values)
- Raised agent answer accuracy from [X]% to [Y]% on a [N]-question eval by adding a metric registry with retrieval.
- Improved retrieval recall@[k] from [X] to [Y] using hybrid search and reranking on a [N]-pair labeled set.
- Trained a win-probability model with a Brier score of [X] (calibrated, grouped cross-validation by game), beating a logistic baseline by [Z].
- Cut p95 latency on [endpoint] from [X] ms to [Y] ms with Redis caching, load-tested at [N] concurrent users, and deployed on AWS with GitHub Actions CI and an eval regression gate.
