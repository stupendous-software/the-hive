# API Integration

clone exposes a RESTful API and a WebSocket interface for programmatic control, enabling tight integration with external systems.

## Base URL
- HTTP API: `http://localhost:50080/api`
- WebSocket: `ws://localhost:50080/ws`

## Authentication
Modes:
- None (local only)
- Bearer token (set `A0_API_KEY` environment variable)
- OAuth2 (optional, for external access)

## Core HTTP Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/agent/run` | Send a prompt and get a response |
| GET | `/agent/status` | Current agent status and memory stats |
| POST | `/memory/save` | Store a memory fragment |
| GET | `/memory/search?query=...` | Semantic recall |
| POST | `/project/switch` | Switch active project |
| GET | `/metrics` | Prometheus metrics |
| GET | `/health` | Health check |

### Example: Simple Prompt
```bash
curl -X POST http://localhost:50080/api/agent/run \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"What is the weather in Paris?"}'
```

## Call Subordinate Programmatically
You can instruct the agent to spawn sub‑agents using the `call_subordinate` tool in the prompt or via the `/agent/run` endpoint. Example payload:
```json
{
  "prompt": "Use call_subordinate with profile='researcher' to find latest AI news and summarize."
}
```
The agent will handle delegation and return the subordinate’s response.

---

## Agent-to-Agent (A2A)
clone implements the FastA2A protocol, allowing secure communication with other agents. Use the `a2a_chat` tool to send messages and files.

## Webhooks
Configure webhooks to trigger external HTTP endpoints on events (e.g., task completion, error). Set `A0_WEBHOOK_URL` in the environment or via the API.

## Scheduler
Tasks can be scheduled declaratively using the task scheduler subsystem. Examples:
- Run every 5 minutes: `*/5 * * * *`
- Run at a specific datetime: `2026-03-08T18:25:00`

Controls: `scheduler:list_tasks`, `scheduler:run_task`, etc.

---

## Client Libraries
While raw HTTP calls work, community SDKs may exist. Check the skills marketplace for integration helpers.

