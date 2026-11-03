# Session prompts

Paste one at the start of a coding-agent session. All assume `AGENTS.md` is in the repo root. Replace bracketed parts. Default mode is guided; add "mode: build" for scaffolding-heavy sessions.

## M0: Setup
```
Read AGENTS.md and docs/MILESTONES.md (M0). Scaffold the monorepo from docs/REPO_STRUCTURE.md, a Docker Compose file with Postgres (pgvector) and Redis, a FastAPI /healthz endpoint, and a GitHub Actions workflow for ruff and pytest. Create .gitignore (with .env) and .env.example first. mode: build
```

## M1: Data and schema
```
Read docs/DATA_SCHEMA.md and docs/MILESTONES.md (M1). First inspect the real nflverse play-by-play columns for [season] and propose adjustments to the draft schema. Do not guess column names. Then help me write the Alembic migration and an idempotent ingestion job. Guided mode: you scaffold, I write the transformation logic.
```

## M2: Contextual layer and baseline agent
```
Read docs/METRIC_REGISTRY.md, docs/AGENT_DESIGN.md, docs/EVALUATION.md. Scaffold the registry loader, the tool schemas, the SQL guardrail module skeleton, and the eval harness runner. I will write the agent loop, the planner prompt, and the guardrail logic. Give me hints and review my code rather than writing those parts.
```

## M3: ML models
```
Read docs/ML_PLAN.md. Scaffold ml/ (feature module stubs, training entry points, S3 registry helpers, tests including a no-leakage test). I will write the features, the grouped cross-validation, and the Optuna objective. Ask me questions that lead me to a calibrated model, and review my results for leakage.
```

## M4: RAG
```
Read docs/RAG_DESIGN.md and docs/EVALUATION.md. Scaffold rag/ and the retrieval eval runner. I will implement chunking variants, hybrid retrieval with rank fusion, and reranking. Help me design the ablation table and check my labeling approach.
```

## M5: Production layer
```
Read docs/API_SPEC.md and docs/INFRA_AND_CICD.md. Scaffold Redis caching with versioned keys, RQ jobs, JWT auth, rate limiting, and the WebSocket replay endpoint. Then write a k6 script. I will decide cache keys and invalidation rules. Ask me about the trade-offs before implementing. mode: build for the boilerplate.
```

## M6: Web app
```
Read docs/API_SPEC.md. Build the React/TypeScript chat UI with streaming and citations, a win-probability chart, and an eval dashboard page. mode: build
```

## M7: Deploy
```
Read docs/INFRA_AND_CICD.md. Write Dockerfiles, the CI eval gate, and the deploy workflow for [EC2/ECS]. Review IAM and security group settings with me. mode: build
```

## Generic prompts
Debugging:
```
Here is the failing test and traceback: [paste]. Before proposing a fix, tell me your top two hypotheses and how I could check each.
```
Code review:
```
Review my change against docs/CODING_STANDARDS.md and the relevant design doc. List issues by severity. Do not rewrite the code.
```
Eval failure analysis:
```
Here are the failing golden questions and traces: [paste]. Group the failures by root cause (wrong metric, bad SQL, bad routing, retrieval miss, hallucination) and suggest what to change first.
```
Resume bullets:
```
Using only the numbers in docs/RESULTS_LOG.md, draft four resume bullets. Do not add any number or tool that is not in the log.
```
