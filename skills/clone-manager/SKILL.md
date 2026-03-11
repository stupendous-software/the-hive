name: clone-manager
description: Enhanced clone management with functional controls, A2A communication configuration, and distinct listing (clones vs agents).
version: 1.0.0
author: clone
tags:
  - docker
  - clone
  - a2a
allowed_tools:
  - code_execution_tool
---
# Clone Manager Skill

## Overview
Provides comprehensive management of clone clones including start, stop, restart, delete (with confirmation), and automatic A2A protocol configuration for inter-agent communication.

## Tools

### list_clones
List all clone containers (excludes self). Returns a markdown table with status, port, memory subdir, and action icons.

### list_agents
List all clone containers (includes self).

### start_container <container_name>
Start a stopped container. No confirmation required.

### stop_container <container_name>
Stop a running container. No confirmation required.

### restart_container <container_name>
Restart a container. No confirmation required.

### delete_container <container_name>
Delete a container with confirmation. Prompts user for Y/N before deletion.

### configure_a2a <container_name|self>
Enable A2A server in the specified container's settings.json and restart it. For 'self', configures current agent.

## Implementation Details
- Detects self container: name='agent0' or from Docker PID 1 check
- Clone containers: names matching 'agent-*' or 'agent-zero-clone-*'
- A2A configuration: sets `a2a_server_enabled=true` and `a2a_server_port=8000` in settings.json via environment variable or direct file edit
- Uses Docker commands for container lifecycle
- Icons: ▶️ start, ⏹️ stop, 🔄 restart, 🗑️ delete

## Usage
First, enable A2A on self:
```json
{"tool_name":"clone-manager:configure_a2a","tool_args":{"container_name":"self"}}
```
Then configure clones:
```json
{"tool_name":"clone-manager:list_clones"}
```
And apply A2A to each clone as needed.
