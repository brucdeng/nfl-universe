#!/usr/bin/env bash
set -euo pipefail

# Cluster bootstrap only. Application schema and vector extension activation
# belong in Alembic migrations in M1. This runs only on an empty data volume.
psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" --set ON_ERROR_STOP=1 \
  --set app_password="$APP_DB_PASSWORD" --set agent_password="$AGENT_DB_PASSWORD" <<'SQL'
CREATE ROLE app_rw LOGIN PASSWORD :'app_password' NOSUPERUSER NOCREATEDB NOCREATEROLE;
CREATE ROLE agent_ro LOGIN PASSWORD :'agent_password' NOSUPERUSER NOCREATEDB NOCREATEROLE;
ALTER ROLE agent_ro SET default_transaction_read_only = on;
REVOKE ALL ON DATABASE nfl_universe FROM PUBLIC;
GRANT CONNECT ON DATABASE nfl_universe TO app_rw, agent_ro;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO app_rw, agent_ro;
SQL
