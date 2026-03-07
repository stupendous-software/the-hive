---
name: agent-clone
description: Spawn a new Hive clone (sub-agent) from the parent agent. Uses the brianheston/the-hive:beta Docker image with proper volume layering and heartbeat coordination. Use when the user requests a new clone or when automatic scaling is needed.
version: 1.0.0
author: Hive Team
tags:
  - docker
  - deployment
  - hive
allowed_tools:
  - code_execution_tool
---

# Agent Clone Skill (Hive)

This skill allows the Hive parent agent to spawn new clone sub-agents automatically. It uses the custom Hive Docker image `brianheston/the-hive:beta` and follows the Hive volume naming conventions.

## When to Use

- When the user explicitly asks for a new sub-agent or clone.
- When the system requires additional parallel agents.

## Procedure

1. Choose a unique `clone_name` (alphanumeric and hyphens) for the new clone. This will become its memory subdirectory and container name prefix.
2. Determine an available host port for the clone's web UI (or let the parent decide a free port).
3. Execute the clone script via `code_execution_tool`:

```json
{
  "tool_name": "code_execution_tool",
  "tool_args": {
    "runtime": "terminal",
    "session": 0,
    "reset": false,
    "code": "python /a0/skills/agent-clone/scripts/clone.py <port> <clone_name>"
  }
}
```

Replace `<port>` and `<clone_name>` with the actual values.

4. Wait for the tool response. On success, the clone container will start and begin sending heartbeats to the shared `hive_heartbeat` volume. The parent manager (`parent_clone_manager.py`) will automatically detect and monitor the new clone.

## Notes

- The script uses the following Docker resources:
  - Image: `brianheston/the-hive:beta`
  - Base data volume: `hive_data` (read-only)
  - Clone overlay volume for `/a0/usr`: `hive_clone_<clone_name>`
  - Logs volume: `hive_logs_<clone_name>`
  - Temp volume: `hive_tmp_<clone_name>`
  - Heartbeat volume: `hive_heartbeat`
  - A2A secret volume: `hive_secrets` (mounted as `/a0/usr/.secrets`)
- Environment variables set: `A0_CLONE_NAME=<clone_name>`, `A0_CLONE_MEMORY_SUBDIR=<clone_name>`, `A0_CLONE_PORT=<port>`.
- The parent manager enforces policies: max 5 active clones, idle timeout 15 minutes, and Recoverable state before removal.
- The parent manager reads policy files `/a0/usr/git_policy.md` and `/a0/usr/handbook/CLONE_HANDBOOK.md` if present and broadcasts changes via A2A.
