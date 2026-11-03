# API spec (draft)

Base path `/v1`. JSON unless noted. All routes except `/healthz` and `/auth/*` require a bearer JWT. Rate limits are per user and enforced in the gateway.

| Method | Path | Purpose |
|---|---|---|
| GET | `/healthz` | Liveness and dependency checks |
| POST | `/auth/register`, `/auth/login` | Create account, get token |
| POST | `/agent/ask` | Ask a question (supports streaming via SSE) |
| GET | `/games` | List games (filters: season, week, team) |
| GET | `/games/{game_id}/winprob` | Win-probability series for a game |
| WS | `/games/{game_id}/replay` | Real-time replay with probability updates and anomaly flags |
| POST | `/ml/winprob` | Predict from a game state (batch supported) |
| GET | `/metrics` | List registry metrics |
| GET | `/evals/latest` | Latest eval and model results for the dashboard |

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
