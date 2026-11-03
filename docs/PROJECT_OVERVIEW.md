# Project overview

## Goal
Build one deployed application that demonstrates backend engineering, AI engineering (agents, RAG, evals), and ML (training, tuning, validation) on NFL data, with measured results.

## What it does
1. Answers questions in plain English ("Which teams improved most on third down after week 6?") by planning, querying, computing, charting, and explaining.
2. Retrieves from text documents when stats alone can't answer ("Why did the passing offense drop in week 9?"), with citations.
3. Serves live win probability (replaying historical games at real-time speed) and flags statistically unusual plays.

## Scope
In scope for v1:
- One completed NFL season of play-by-play data.
- 10 to 15 documented metrics in a metric registry.
- One or two document sources (check terms before ingesting).
- Three ML models: win probability, one regression, one anomaly detector.
- Eval harness, load test, CI gate, AWS deployment, web UI.

Out of scope for v1 (stretch):
- NBA data.
- Roster/lineup optimizer (clustering + OR-Tools).
- Multimodal module over self-generated charts.
- Terraform, Kubernetes, fine-tuning.

## Skills this project must demonstrate
| Skill | Where |
|---|---|
| LLM agents with tool use and planning | `agent/` |
| Contextual layer (metadata, metric definitions) | `agent/` + `metric_registry` table |
| RAG: chunking, hybrid search, reranking, citations | `rag/` |
| ML: classification, regression, anomaly detection | `ml/` |
| Hyperparameter tuning, cross-validation, calibration | `ml/` |
| Evaluation and ablations | `evals/` |
| Backend: API, SQL, caching, queues, auth | `api/`, `ingest/` |
| Infra: Docker, CI/CD, AWS, observability, load testing | `infra/` |

## Success criteria
- Golden-question eval with a recorded baseline, a with/without contextual-layer ablation, and a CI regression gate.
- Retrieval eval with recall@k and MRR and an ablation table.
- Win-probability model beats its baseline, with Brier score and a calibration plot.
- Load test shows p50/p95 latency before and after caching.
- Live URL, README with architecture diagram, 2 to 3 minute demo video.

## Resume bullet targets
Templates live in `RESULTS_LOG.md`. Only fill them with measured numbers.
