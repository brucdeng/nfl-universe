# Data schema (draft)

This is a starting point. Inspect the real nflverse play-by-play data dictionary and adjust column names and types before writing migrations. Team abbreviations can differ across seasons and sources, so verify them.

## Core tables
```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE teams (
  team_abbr TEXT PRIMARY KEY,
  team_name TEXT,
  conference TEXT,
  division TEXT
);

CREATE TABLE games (
  game_id TEXT PRIMARY KEY,
  season INT NOT NULL,
  week INT,
  game_type TEXT,
  gameday DATE,
  home_team TEXT,
  away_team TEXT,
  home_score INT,
  away_score INT
);

CREATE TABLE plays (
  game_id TEXT NOT NULL REFERENCES games(game_id),
  play_id INT NOT NULL,
  season INT NOT NULL,        -- denormalized for faster filters
  week INT NOT NULL,          -- denormalized
  qtr INT,
  down INT,
  ydstogo INT,
  yardline_100 INT,
  game_seconds_remaining INT,
  posteam TEXT,
  defteam TEXT,
  play_type TEXT,
  yards_gained INT,
  is_pass BOOLEAN,
  is_rush BOOLEAN,
  first_down BOOLEAN,
  score_differential INT,
  posteam_timeouts_remaining INT,
  defteam_timeouts_remaining INT,
  epa DOUBLE PRECISION,
  success BOOLEAN,
  wp DOUBLE PRECISION,        -- external benchmark only, never a model feature
  play_desc TEXT,
  PRIMARY KEY (game_id, play_id)
);
```
Start with the columns the starter metrics need and add more only when a question requires them.

## Indexes to evaluate (measure with EXPLAIN ANALYZE)
- `plays (season, week)`
- `plays (posteam, season)`
- `plays (game_id, play_id)` (primary key already covers this)
- partial indexes on pass/rush plays if scans dominate

## Contextual-layer tables
```sql
CREATE TABLE metric_registry (
  metric_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  definition TEXT NOT NULL,
  sql_expression TEXT NOT NULL,
  grain TEXT,
  caveats TEXT,
  source_tables TEXT[],
  version INT DEFAULT 1,
  embedding vector(384)       -- dimension depends on the embedding model
);

CREATE TABLE schema_descriptions (
  table_name TEXT NOT NULL,
  column_name TEXT,           -- NULL means table-level description
  description TEXT NOT NULL,
  embedding vector(384),
  PRIMARY KEY (table_name, column_name)
);
```

## RAG tables
```sql
CREATE TABLE docs (
  doc_id BIGSERIAL PRIMARY KEY,
  source TEXT NOT NULL,
  title TEXT,
  url TEXT,
  published_at TIMESTAMPTZ,
  license TEXT,
  metadata JSONB DEFAULT '{}'
);

CREATE TABLE doc_chunks (
  chunk_id BIGSERIAL PRIMARY KEY,
  doc_id BIGINT NOT NULL REFERENCES docs(doc_id),
  chunk_index INT NOT NULL,
  text TEXT NOT NULL,
  embedding vector(384),
  tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', text)) STORED,
  metadata JSONB DEFAULT '{}'   -- team, player, date, section
);
CREATE INDEX doc_chunks_tsv_idx ON doc_chunks USING GIN (tsv);
CREATE INDEX doc_chunks_vec_idx ON doc_chunks USING hnsw (embedding vector_cosine_ops);
```

## Eval tables
```sql
CREATE TABLE eval_runs (
  run_id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT now(),
  git_sha TEXT,
  suite TEXT,
  config JSONB,
  metrics JSONB
);

CREATE TABLE eval_results (
  run_id BIGINT REFERENCES eval_runs(run_id),
  question_id TEXT,
  passed BOOLEAN,
  score DOUBLE PRECISION,
  latency_ms INT,
  cost_usd NUMERIC(10,5),
  trace_url TEXT,
  details JSONB,
  PRIMARY KEY (run_id, question_id)
);
```

## Roles
- `app_rw`: used by API and ingestion.
- `agent_ro`: SELECT only on an allowlist of tables. The agent's SQL tool connects with this role only.
