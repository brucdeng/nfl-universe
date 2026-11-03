# Results log

Record every measurement here with the date, git SHA, and config. Only write numbers you measured. Resume bullets are drafted from this file.

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
