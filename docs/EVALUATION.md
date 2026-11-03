# Evaluation

## Suites
| Suite | What it measures |
|---|---|
| Golden agent questions | Execution accuracy, metric-definition correctness, latency, cost |
| Retrieval | recall@k, MRR |
| Answer grounding | Faithfulness and citation accuracy |
| Routing | Whether the agent picked the right tool(s) |
| ML | Accuracy, Brier, calibration, regression error |
| Safety | Prompt-injection and SQL-guardrail tests |
| Load | p50/p95 latency, throughput, cache hit rate |

## Golden question format (`evals/golden/*.jsonl`)
```json
{
  "id": "g001",
  "question": "...",
  "category": "aggregate | ranking | comparison | metric_definition | multi_step | rag | ml | unanswerable | injection",
  "expected_tools": ["run_sql"],
  "expected_answer": {"type": "number", "value": 0.0, "tolerance": 0.001},
  "reference_sql": "SELECT ...",
  "notes": "verified by hand on DATE"
}
```
Verify every expected answer yourself against the data. Do not take expected values from the model.

## Scoring
- Numeric and table answers: compare result sets with tolerance (execution accuracy), not SQL text.
- Free-text answers: rubric-based LLM judge, spot-checked by hand on a sample each run. Record judge agreement with your own labels.
- Citations: check that cited chunks exist and support the claim.
- Routing: compare tools used with `expected_tools`.

## Starter question ideas (write the real versions after data is loaded)
1. Which team had the highest EPA per play in a given week?
2. Top five teams by third-down conversion rate for the season.
3. Compare two teams on explosive play rate.
4. What does "success rate" mean in this app? (metric_definition)
5. How did a team's pass rate change before and after week 8?
6. Which teams scored the most points per game on the road?
7. Give the win probability for a specified game state. (ml)
8. Which plays in a given game were most anomalous? (ml)
9. Why did a team's offense decline in a given stretch? (rag + sql)
10. What does the rulebook say about a specific situation? (rag)
11. A question about a different season than the data covers. (unanswerable)
12. A vague question like "who is the best team?" (should ask for a definition)
13. A question whose retrieved document contains an injected instruction. (injection)
14. A request to modify data or drop a table. (safety)
15. A question that needs a metric not in the registry. (should flag ad hoc)
Target about 30 by M2 and grow as failures appear.

## Ablations (required results)
| Ablation | Variants |
|---|---|
| Contextual layer | none, schema only, schema + metric registry |
| Retrieval | see `RAG_DESIGN.md` |
| Model choice for the agent | small vs larger model (accuracy, cost, latency) |
| Caching | on vs off |

## CI gate
- `make eval` runs the fast suite on every PR using a small, deterministic subset.
- Fail the build if golden accuracy drops by more than 3 points absolute, or retrieval recall@5 drops by more than 3 points, versus the last main-branch run. Tune thresholds after you see run-to-run variance.
- Pin the model version and set temperature to 0 for evals. Account for remaining nondeterminism with repeated runs on flaky items.
- Store each run in `eval_runs` and `eval_results` with git SHA and prompt version.
- The full suite runs nightly or on demand to control cost.

## Reporting
`evals/report.py` produces a markdown table per run and appends headline numbers to `docs/RESULTS_LOG.md` when the owner approves.
