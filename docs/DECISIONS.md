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
