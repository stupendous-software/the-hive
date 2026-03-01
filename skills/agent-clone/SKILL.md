---
name: agent-clone
description: Spawn a new Agent Zero instance with the same skills and configuration but with isolated memory and chat storage. Uses Docker to create the new container, copying settings and custom scripts while keeping the memory subdirectory separate.
version: 1.0.0
author: Agent Zero
tags:
  - docker
  - deployment
  - cli
allowed_tools:
  - code_execution_tool
---

# Agent Clone Skill

## Overview
This skill creates a new Agent Zero container that shares your global skills and preferences but maintains separate memory, chats, and project data. It's ideal for testing, scaling, or running parallel agents.

## Usage
Execute the clone script with the required port and optional memory subdir:

```bash
python scripts/clone.py <port> [memory_subdir]
```

- `<port>`: Host port to expose the new agent's web UI (e.g., `50082`).
- `[memory_subdir]`: Optional memory subdirectory name (default: `clone`).

Example:
```bash
python scripts/clone.py 50082 test_instance
```

## Implementation Details
The script performs:
1. Creates a new host directory `/a0/usr_clone` (or a custom path if advanced parameters are needed).
2. Copies `/a0/usr/settings.json`, any `secrets.env`, and the entire `/a0/usr/scripts` tree into the new directory.
3. Creates fresh `memory/` and `projects/` directories to ensure zero overlap.
4. Starts a new container with Docker, mounting:
   - Global skills (read-only)
   - Cloned settings/scripts (read-only)
   - Fresh `memory/` and `projects/` directories (read-write)
   - Environment variable `A0_SET_agent_memory_subdir=<memory_subdir>` to ensure isolation.

## Customization
You can edit `scripts/clone.py` to change the base image, add extra volumes, or enable project sharing.
