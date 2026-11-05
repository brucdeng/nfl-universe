# API spec (draft)

Business routes use base path `/v1`; health routes are at the root. JSON unless
noted. Only `/healthz` and `/livez` are implemented in M0. Planned business routes
require a bearer JWT except `/auth/*`; authentication and rate limits arrive in M5.

| Method | Path | Purpose |
|---|---|---|
| GET | `/healthz` | Dependency readiness: Postgres query, pgvector availability, Redis PING |
| GET | `/livez` | API process liveness, without dependency calls |
| POST | `/auth/register`, `/auth/login` | Create account, get token |
| POST | `/agent/ask` | Ask a question (supports streaming via SSE) |
| GET | `/games` | List games (filters: season, week, team) |
| GET | `/games/{game_id}/winprob` | Win-probability series for a game |
| WS | `/games/{game_id}/replay` | Real-time replay with probability updates and anomaly flags |
| POST | `/ml/winprob` | Predict from a game state (batch supported) |
| GET | `/metrics` | List registry metrics |
| GET | `/evals/latest` | Latest eval and model results for the dashboard |

## Health endpoints (implemented)
`GET /healthz` returns HTTP 200 when all checks pass:
```json
{"status":"ok","checks":{"postgres":"ok","pgvector":"ok","redis":"ok"}}
```
Dependency failures return HTTP 503 with `status: "error"` and affected checks
set to `"error"`. Responses and health logs omit driver exception details and
connection credentials. Database connection/pool/statement waits and Redis socket
waits are bounded; Redis health requests do not retry automatically.

The pgvector probe checks `pg_available_extensions`, not activation in the current
database. M1 migrations will activate the extension. `GET /livez` returns HTTP 200
with `{"status":"ok"}` without calling either dependency.

## POST /agent/ask
Request:
```json
{"question": "string", "conversation_id": "optional string", "stream": true}
```
Response (non-streaming) follows the `Answer` schema in `AGENT_DESIGN.md`, plus:
```json
{"trace_id": "string", "latency_ms": 0, "cached": false}
```
Streaming events: `plan`, `tool_call`, `tool_result`, `token`, `final`.

## WS /games/{game_id}/replay
Query params: `speed` (1 = real time). Server messages:
```json
{"type": "play", "play_id": 0, "desc": "...", "win_prob": 0.0, "anomaly": false}
{"type": "done"}
```

## Errors
Consistent body: `{"error": {"code": "string", "message": "string"}}`. Use 400 for validation, 401/403 for auth, 429 for rate limits, 504 for tool timeouts.

## Caching
- Cache key = route + normalized params + data version (bumped on ingestion).
- Agent answers: cache only when no ML live state is involved; short TTL.
- Never cache across users for authenticated personal data.
