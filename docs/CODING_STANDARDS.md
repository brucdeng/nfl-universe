# Coding standards

## Python
- Python 3.11+, type hints on all public functions, `ruff` for lint and format.
- Pydantic v2 models for all external inputs and tool schemas.
- Keep I/O at the edges. Put logic in pure functions that are easy to test.
- Use dependency injection (FastAPI `Depends`) for DB sessions and clients.
- No bare `except`. Raise specific errors and return structured errors from tools.
- Config via environment variables loaded in one settings module.
- Structured logging, no `print` in library code.

## SQL and migrations
- Alembic migrations only. Each migration is reversible when practical.
- Parameterized queries. No string-formatted SQL with user input.
- Name indexes and constraints explicitly.

## ML code
- Deterministic seeds, logged library versions.
- Feature functions are pure and tested. Include a test that forbidden (leaky) columns are absent from the feature set.
- Splits are grouped by game. Never shuffle plays across games.
- Notebooks for exploration only.

## Agent code
- Prompts live in versioned files, not inline strings.
- Every tool has a Pydantic input and output schema and a unit test.
- Never execute model-produced SQL or code without the guardrails.
- Truncate large tool outputs before returning them to the model.

## TypeScript / React
- Strict TypeScript. No `any` without a comment.
- Typed API client generated or hand-written from `API_SPEC.md`.
- Keep components small. Handle loading, error, and empty states.
- No secrets in the frontend.

## Testing
- Unit tests for pure logic, integration tests for DB and Redis using test containers or CI services.
- Agent tests use recorded or stubbed LLM responses for determinism. Real-LLM tests live in the eval harness, not unit tests.
- Bug fixes include a regression test.

## Git
- Small commits, imperative messages ("Add hybrid retrieval"), one logical change each.
- Branch per milestone task, PR to main, CI must pass.
- Never commit data dumps, model binaries, or secrets.

## Documentation
- Update the relevant doc in `docs/` when behavior or design changes.
- Add an entry to `DECISIONS.md` for any non-obvious choice.
