# Usage Guide

Agent Zero offers several interfaces: the Web UI (primary), local terminal (debug), and programmatic API.

## Web Interface

### Access

Open `http://localhost:50080` after starting the agent. The UI includes:

- Conversation view with real-time streaming
- Memory browser and AI recall
- Project switcher
- Settings (LLM, memory, providers)
- Live logs via WebSocket
- File browser
- Tunnel status and URL

### Interacting

Type in the chat input. The agent will:

1. Understand your intent
2. Plan and use tools automatically (browser, code execution, memory, etc.)
3. Stream the response

You can intervene at any time; the agent respects the conversation history.

### Key Tools

- **browser_agent** – Browse websites, take screenshots, extract text.
- **code_execution** – Run Python/JavaScript in a sandbox.
- **file_operations** – Read/write files in the agent's workspace.
- **memory_save / memory_load** – Explicit memory storage and retrieval.
- **scheduler** – Create and manage scheduled tasks.
- **wait** – Pause execution for a duration or until a specific time.
- **call_subordinate** – Spawn a specialized subordinate agent.
- **mcp_client** – Connect to external MCP servers.
- **webhook** – Send notifications to external services.
- **search_engine** – Perform web searches.
- **document_query** – Q&A over documents (PDF, DOCX, HTML).

Tool usage is automatic, but you can explicitly request them (e.g., "Save this to memory").

### Subordinate Agents

Delegate specialized tasks by saying, "Call a researcher to find latest AI news." The agent uses `call_subordinate` with the appropriate profile.

Available profiles: `coder`, `researcher`, `hacker`, `writer`, `analyst`. Custom profiles can be created in Settings → Profiles.

### Projects

Projects isolate memory, instructions, and secrets.

- Create a project via UI → Projects or API.
- Switch projects to change context.
- Each project has its own folder under `a0/usr/projects/`.

Use projects for multi-client work, personal vs. work separation, or experimentation.

### Memory

- **Automatic**: The agent saves notable events automatically.
- **Manual**: Use `memory_save("...")` to store explicit facts.
- **Recall**: Relevant memories are automatically injected into prompts. You can also `memory_load` manually.

Adjust recall behavior in Settings → Memory (interval, embedding model).

### Skills

Skills extend functionality (new tools, UI panels). Install via UI → Skills → Marketplace or manually place under `a0/usr/skills/`. Manage them in Settings → Skills.

For creating skills, see the [Skills Guide](./skills.md).

### Connectivity

- **MCP**: Agent Zero can act as an MCP server or connect to external MCP servers. Enable in Settings → MCP.
- **A2A**: Secure agent-to-agent communication using FastA2A. Configure in Settings → A2A.

### Scheduler & Tasks

Schedule recurring or one-off tasks. Example: "Remind me every Monday at 9am to review logs." The scheduler creates a task that runs in the background.

## Local Terminal (CLI)

For headless or scripted use:

```bash
python a0/agent.py --headless
```

Input is read from stdin; output goes to stdout.

## Programmatic API

```python
from python.api.agents import AgentContext

ctx = AgentContext(config=None, name="my_agent", set_current=True)
agent = ctx.agent0
result = agent.run("Your task here")
print(result)
```

For advanced usage (multiple contexts, memory access), see [API Integration](./api-integration.md).

## Remote Access via Tunneling

Quickly expose the Web UI via tunnel:

1. In Settings → Tunnel enable a provider (e.g., Cloudflare Tunnel, ngrok).
2. Provide required credentials (stored in secrets).
3. The agent will display a public URL.

> **Security:** Always use strong passwords and HTTPS. Tunnels are convenient but may expose the agent; limit access.

Alternatively, set up your own reverse proxy (Nginx) with SSL in front of the Docker container.

## Tips

- Be specific and iterative in prompts.
- Let the agent use its tools; it's designed for tool-augmented reasoning.
- Monitor logs and metrics for performance.
- Backup `a0/usr/` regularly.
- Use projects to separate concerns.

## Troubleshooting

See [Troubleshooting](./troubleshooting.md).
