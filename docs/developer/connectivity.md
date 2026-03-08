# Connectivity (MCP & A2A)

Agent Zero supports modern AI protocols for interoperability.

## MCP (Model Context Protocol)

### As Server

Agent Zero can expose its tools as an MCP server. Enable in Settings → MCP Server. The server runs via streamable HTTP (default port configurable). External clients can then call Agent Zero’s tools.

### As Client

Agent Zero can connect to external MCP servers to extend its capabilities. Configure the server URL in Settings → MCP Clients. Once added, the server’s tools become available to the agent.

Configuration is stored in `settings.json` under `mcp`. Environment variables can set initial values: `A0_SET_mcp_enabled=true` and `A0_SET_mcp_server_host=localhost`.

## A2A (Agent-to-Agent)

FastA2A protocol allows Agent Zero instances to communicate directly.

- **Server mode**: Enable in Settings → A2A. Provides a secret for authentication. Other agents can connect as clients.
- **Client mode**: Add remote A2A agent URL and secret. The remote’s tools become available via `call_remote_agent` tool.

Environment variables: `A0_SET_a2a_server_enabled=true`, `A0_SET_a2a_secret=your-secret`.

## Debugging

- Check `/status` for connectivity health.
- Enable debug logging for protocol traces.
- Verify network/firewall allows required ports.
- Use `a0_status` CLI to view active connections.
