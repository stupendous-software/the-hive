# Cloning UI Form — Specification

## Overview
A dedicated page in the Agent Zero Web UI to configure and spawn a new clone, selecting its parent agent.

## Form Layout

- **Parent Agent** (dropdown)
  - Options: available parent agents from heartbeat registry.
  - Disabled if parent.current_clones >= parent.max_clones.
  - Hover tooltip: "X/Y clones
List: name1 (port), name2 (port)…"
- **Clone Name** (text)
- **Port** (number, optional; if empty auto‑assign)
- **Memory Subdir** (text, auto‑generated if empty)
- **Project** (dropdown of existing projects)
- **Tags** (multi‑select chips)
- **LLM Override**: Provider (select), Model (text), API Key (password)
- **Resources**: CPU (slider 0.1–4), Memory (slider GB), PIDs (number)
- **Tool Whitelist** (multi‑select multi‑choose)
- **Network Policy** (select: none, allowlist, denylist)
- **Heartbeat Interval** (number, seconds)
- **Auto‑Update** (checkbox)
- **Log Level** (select: DEBUG, INFO, WARNING, ERROR)

## Backend API

### GET /api/clone/parents
Response:
```json
[
  {
    "uuid": "57a27a2d6f78",
    "name": "Number One",
    "port": 42437,
    "current_clones": 3,
    "max_clones": 5,
    "clones": [
      {"name": "agent-zero-clone-Q", "port": 46801, "status": "active"},
      {"name": "agent-Atlas", "port": 50013, "status": "active"}
    ]
  }
]
```

### POST /api/clone/create
Payload (JSON): see form fields combined.
Response: `{ "success": true, "uuid": "...", "port": 50015, "container_id": "..." }`.

## Integration
- Frontend located at `/webui/pages/cloning.html`.
- Backend router in `/python/api/clone_api.py` (FastAPI).
- Router to be included in main app (e.g., `app.include_router(clone_router)`).

## Security
- Require authenticated session.
- Rate limit per user.
- Validate and sanitize all inputs.

