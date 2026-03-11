name: clone-heartbeat-monitor
description: Monitors clone agents for health status, collects logs from failed clones, and sends alerts.
version: 1.0.0
author: clone
tags:
  - monitoring
  - health
  - logs
  - alerts
allowed_tools:
  - code_execution_tool
  - notify_user
---

# Clone Heartbeat Monitor Skill

## Overview
This skill provides proactive monitoring of clone clones. It detects offline clones, retrieves their logs, and notifies the user with diagnostic information.

## Usage
Run the monitor script manually or schedule it:

```bash
python scripts/monitor.py
```

The script will:
- Discover all clone containers (named 'agent-*')
- Check their health status via Docker
- If a clone is not running or health check fails, collect recent logs
- Send a notification with findings

## Integration with Scheduler
To monitor regularly, create a scheduled task:

```json
{
  "name": "Clone Heartbeat Monitor",
  "type": "scheduled",
  "schedule": {"minute": "*/5", "hour": "*", "day": "*", "month": "*", "weekday": "*"},
  "prompt": "Run the clone heartbeat monitor: python /a0/skills/clone-heartbeat-monitor/scripts/monitor.py"
}
```

## Implementation Details
- Uses `docker ps -a --filter 'name=agent-*'` to discover clones
- Health check: attempts to curl `http://localhost:<port>/health` (port mapped from container)
- Log collection: `docker logs --tail 100 <container_name>`
- Notifications: `notify_user` tool with 'warning' or 'error' severity
