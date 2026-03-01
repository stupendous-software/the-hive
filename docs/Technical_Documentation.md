# Agent Zero Framework - Complete Technical Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Architecture Overview](#architecture-overview)
3. [Installation & Setup](#installation--setup)
4. [Configuration](#configuration)
5. [Core Features](#core-features)
6. [Projects & Isolation](#projects--isolation)
7. [Skills System](#skills-system)
8. [API Integration](#api-integration)
9. [Web UI & WebSocket Infrastructure](#web-ui--websocket-infrastructure)
10. [Security Considerations](#security-considerations)
11. [Development & Customization](#development--customization)
12. [Troubleshooting](#troubleshooting)
13. [Reference Materials](#reference-materials)

---

## Introduction

**Agent Zero** is a Dockerized, containerized AI agent framework that enables autonomous, tool-using AI assistants with sophisticated capabilities including:

- Multi-modal interactions (text, voice, vision)
- Real-time WebSocket communication with streaming outputs
- Comprehensive tool ecosystem (file operations, browser automation, code execution, etc.)
- Project-based isolation with separate memory, instructions, and secrets
- Skill-based extensibility for specialized tasks
- Remote agent-to-agent (A2A) communication
- Model Context Protocol (MCP) support
- Full Web UI with real-time output and chat management

**Version**: v0.9.8 (as of system date: 2026-02-28)

### Key Characteristics

- **No coding required**: Operate entirely through natural language prompting
- **Fully Dockerized**: Runs in isolated container environment
- **Root access**: Full Linux terminal capabilities within container
- **Streaming outputs**: Real-time response streaming for immediate feedback
- **Persistent memory**: Long-term knowledge storage with semantic search
- **Multi-LLM support**: Compatible with various model providers

---

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Browser / Client                    │
└────────────────────────────┬──────────────────────────────┘
                             │ WebSocket
┌────────────────────────────▼──────────────────────────────┐
│              WebSocket Handler (FastAPI)                  │
│  • Connection management                                  │
│  • Message envelope parsing                              │
│  • Event streaming                                        │
└────────────────────────────┬──────────────────────────────┘
                             │
┌────────────────────────────▼──────────────────────────────┐
│               Agent Zero Core (Python)                    │
│  • Context & conversation management                     │
│  • Tool orchestration & execution                        │
│  • Memory system                                          │
│  • Scheduler                                              │
│  • Project isolation                                      │
└────────────────────────────┬──────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────────┐
│                          Tools & Extensions                              │
├─────────────────────────────────────────────────────────────────────────┤
│ • File operations    • Browser automation  • Code execution             │
│ • Skills system      • A2A communication   • MCP connections           │
│ • Search engine      • Document processing  • External API integration │
└─────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Client Connection**: WebSocket connects to `/ws` endpoint
2. **Message Processing**: Messages parsed into `TextEnvelope` with JSON fields
3. **Agent Processing**: Core agent reads context, chooses tools, executes actions
4. **Tool Execution**: Tools run with appropriate runtime (terminal, python, nodejs)
5. **Response Streaming**: Outputs sent back via WebSocket with real-time updates
6. **Logging**: All interactions saved to logs/ as HTML files

### Technology Stack

- **Backend**: Python, FastAPI, WebSockets
- **Container**: Docker (Debian Kali base)
- **LLM Integration**: OpenRouter, Anthropic, OpenAI, local models (Ollama, LM Studio)
- **Embeddings**: Local sentence-transformers or OpenAI-compatible
- **Speech**: Whisper-based STT, TTS synthesis
- **Frontend**: HTML/JS with WebSocket client

---

## Installation & Setup

### Prerequisites

- Docker & Docker Compose
- 4GB+ RAM (8GB recommended)
- 10GB+ disk space
- Internet connection for API-based LLMs

### Quick Installation Steps

1. **Clone or obtain Agent Zero**:
   ```bash
   # If from GitHub or other source
   git clone <repository-url>
   cd agent-zero
   ```

2. **Configure `.env` file** (optional for defaults):
   ```bash
   # Copy example environment
   cp .env.example .env
   
   # Edit with your preferences
   nano .env
   ```

   Key environment variables:
   - `A0_SERVER_PORT`: WebSocket port (default: 3000)
   - `A0_UI_PORT`: Web UI port (default: 8080)
   - `A0_LLM_PROVIDER`, `A0_LLM_MODEL`, `A0_API_KEY`: LLM configuration
   - `A0_UTILITY_MODEL_PROVIDER`, `A0_UTILITY_MODEL`: For memory tasks

3. **Build and run**:
   ```bash
   docker-compose up -d
   ```

4. **Access interfaces**:
   - Web UI: `http://localhost:8080`
   - WebSocket: `ws://localhost:3000/ws`
   - Terminal logs: `docker logs -f agent-zero`

### First Run Validation

Check that all services are running:
```bash
docker-compose ps
```

Verify WebSocket connection:
```bash
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
     -H "Host: localhost:3000" \
     -H "Origin: http://localhost:8080" \
     http://localhost:3000/ws
```

---

## Configuration

Agent Zero offers multiple configuration layers:

### 1. Web UI Settings (Recommended)

Navigate to **Settings** page in Web UI:

#### Chat Model Settings
- **Provider**: Anthropic, OpenAI, OpenRouter, Ollama, etc.
- **Model Name**: Provider-specific (e.g., `claude-sonnet-4-5` for Anthropic, `anthropic/claude-sonnet-4-5` for OpenRouter)
- **Context Length**: Total token window (e.g., 100k)
- **Context Window Space**: Fraction allocated to chat history
- **API URL**: Custom endpoint for Ollama, LM Studio, etc.

#### Utility Model Configuration
- Separate model for memory summarization and organization
- Must be capable (70B-class recommended, not small 4B models)

#### Embedding Model Settings
- Local `sentence-transformers/all-MiniLM-L6-v2` by default
- Can switch to OpenAI embeddings (`text-embedding-3-small/large`)

#### Speech Options
- Speech-to-text model size
- Language code
- Silence threshold/duration/timeout

#### API Keys
Configure keys for:
- OpenAI
- Anthropic
- OpenRouter
- GitHub Copilot (OAuth flow)
- Other OpenAI-compatible providers

#### Authentication
- UI Login/Password
- Root container password (for SSH)

#### Development Settings
- RFC URLs/ports for remote function calls between instances
- RFC password for secure remote communication

### 2. Environment Variables (A0_SET_*)

Settings can also be controlled via environment variables with `A0_SET_` prefix:

```bash
A0_SET_llm_provider=openrouter
A0_SET_llm_model=anthropic/claude-sonnet-4-5
A0_SET_api_key=sk-...
```

This overrides Web UI settings and is useful for Docker/CI/CD deployments.

### 3. Settings JSON

The application stores settings in internal storage (typically within Docker volume). Direct manipulation is not recommended; use Web UI or env vars.

> **Note**: Settings are NOT configured by pasting JSON into chat messages. That method is deprecated and unsupported since v0.9.7.

---

## Core Features

### Real-Time Streaming

All agent responses are streamed via WebSocket in real-time. Users can:
- Read along as response generates
- Interrupt or modify prompts mid-stream
- See tool execution outputs progressively

Outputs are also automatically saved to HTML files in `logs/` directory for every session.

### Tool System

Agent Zero uses a **tool calling** paradigm where the LLM decides which tools to use based on the task.

#### Built-in Tools

| Tool | Purpose | Runtime |
|------|---------|---------|
| `code_execution_tool` | Execute terminal/Python/Node.js commands | terminal/python/nodejs/output |
| `document_query` | Read and analyze documents (PDF, Office, HTML, etc.) | N/A |
| `search_engine` | Web search via external engine | N/A |
| `browser_agent` | Control headless browser for web tasks | N/A |
| `a2a_chat` | Communicate with other FastA2A agents | N/A |
| `memory_load` / `memory_save` / `memory_forget` | Long-term memory operations | N/A |
| `notify_user` | Send user notifications | N/A |
| `vision_load` | Load images for visual analysis | N/A |
| `call_subordinate` | Spawn specialized sub-agents | N/A |
| `wait` | Pause execution | N/A |
| `scheduler:*` | Task scheduling system | N/A |
| `skills_tool` | Load and use skills | N/A |

#### Tool Execution Runtimes

- **terminal**: Shell commands (bash)
- **python**: Python code blocks
- **nodejs**: JavaScript/Node.js code
- **output**: Wait for long-running process completion

### Memory System

Agent Zero maintains two memory types:

1. **Short-term context**: Conversation history within session
2. **Long-term memory**: Persistent knowledge storage with semantic search

#### Memory Operations

- `memory_save`: Store text with automatic embedding
- `memory_load`: Retrieve by semantic similarity (threshold 0.7 default)
- `memory_delete`: Remove specific memories by ID
- `memory_forget`: Remove memories by query matching

Memory supports metadata filtering (e.g., `area=='main'`, `timestamp<'2024-01-01'`).

### Task Scheduler

Three scheduler task types:

#### Scheduled (Cron)
```json
{
  "type": "scheduled",
  "schedule": {
    "minute": "*/30",
    "hour": "*",
    "day": "*",
    "month": "*",
    "weekday": "*"
  }
}
```

#### Planned (Fixed Datetimes)
```json
{
  "type": "planned",
  "plan": ["2025-04-29T18:25:00", "2025-04-30T18:25:00"]
}
```

#### AdHoc (Manual)
```json
{
  "type": "adhoc"
}
```

**Tool**: `scheduler:create_*_task`, `scheduler:run_task`, `scheduler:wait_for_task`, `scheduler:list_tasks`, etc.

---

## Projects & Isolation

Agent Zero supports **multi-client project isolation** where each project has:
- Isolated memory storage
- Custom agent instructions
- Dedicated secrets/configurations
- Separate conversation context

This prevents context and credential bleed between different client work.

### Project Structure

```
/usr/projects/<project_name>/
├── .a0proj/          # Project configuration & secrets
├── work/             # Project-specific working files
└── (other project data)
```

### Using Projects

- Projects are **activated** by the user (not manipulated by agent)
- Agent operates within the active project context automatically
- Cannot switch projects programmatically (user control only)
- All file writes should respect project boundaries

---

## Skills System

Skills are modular capabilities that extend Agent Zero with:
- Pre-defined instructions (SKILL.md)
- Script files (Python, bash, etc.)
- Configuration templates

### Available Skills

- **agent-clone**: Spawn new Agent Zero instances with Docker, copying settings while isolating memory
- **create-skill**: Wizard for creating new custom skills
- **smtp-email-sender**: Send emails via SMTP with attachments
- **pdf_editing** (mentioned): Extract forms, convert PDFs
- **github_app_verification**: GitHub app integration

### Skill Workflow

1. `skills_tool:list` - Discover available skills
2. `skills_tool:load` - Load skill instructions and file structure
3. `code_execution_tool` - Run skill scripts with proper paths

Skills follow the `agentskills.io` standard.

---

## API Integration

### OpenAI-Compatible Endpoints

Agent Zero supports any OpenAI-compatible API, including:

- Custom gateways
- Z.AI/GLM
- Local LLMs via Ollama (`http://host:11434/v1`)
- LM Studio (`http://host:1234/v1`)
- Azure OpenAI
- vLLM, Text Generation Inference, etc.

Configure under:
- Provider: **OpenAI Compatible**
- API Key: Any valid key for that endpoint
- API URL: Custom endpoint (optional)
- Model Name: Model ID as recognized by the endpoint

### GitHub Copilot

Special OAuth flow:
1. Select **GitHub Copilot** provider
2. Enter first prompt
3. Follow link and code shown in logs
4. Complete authentication in browser
5. Return to Agent Zero

---

## Web UI & WebSocket Infrastructure

### WebSocket Protocol

The WebSocket endpoint (`/ws`) implements a **text envelope** protocol:

#### Sending Messages

Client sends JSON with these fields:
```json
{
  "thoughts": ["agent reasoning steps"],
  "headline": "brief title",
  "tool_name": "tool_to_use",
  "tool_args": {
    "arg1": "value1",
    ...
  }
}
```

Or final response:
```json
{
  "thoughts": [...],
  "headline": "...",
  "tool_name": "response",
  "tool_args": {
    "text": "Final response to user"
  }
}
```

#### Receiving Messages

Server streams multiple messages back:

1. **Thought updates** (intermediate processing)
2. **Tool execution results** (JSON with output)
3. **Final response** (type: `response`)

All messages are newline-separated.

### Envelope Filtering

WebSocket handlers support filtering semantics to control which messages are sent to clients. Configurable in settings.

---

## Security Considerations

### ⚠️ **Agent Zero Can Be Dangerous!**

With proper instruction, Agent Zero can perform potentially harmful actions:
- Modify system files
- Access sensitive data
- Make network requests
- Execute arbitrary code
- Use credentials

**Always run Agent Zero in an isolated environment (Docker)** and be careful what you prompt it to do.

### Containment Strategies

1. **Docker isolation**: Container should not have privileged access to host
2. **Network segmentation**: Limit outbound network access if possible
3. **Credential management**:
   - Use project-specific secrets
   - Never embed secrets in chat history
   - Rotate keys regularly
4. **SSH access**: Set strong root password in UI settings
5. **UI authentication**: Enable UI login/password

### Secure Development

- Never commit secrets to repository
- Use environment variables or secret managers
- Review skills before installing
- Audit tool usage logs

---

## Development & Customization

### Custom Prompts

Since v0.9.7, custom prompts belong in:
```
/a0/agents/<agent_name>/prompts/
```

Instead of shared `/prompts` folder. See **Extensions Guide** for details.

### Extending with New Tools

1. Define tool in `tools/` directory
2. Implement handler function
3. Register in tool registry
4. Add to agent system prompt
5. Update WebSocket protocol if needed

### Creating Skills

Use the `create-skill` skill or follow template:
- `SKILL.md` with metadata and instructions
- `scripts/` for executable code
- `docs/` for skill documentation

### Remote Function Calls (RFC)

Configure in Development Settings:
- RFC URLs/ports for inter-instance communication
- RFC password for authentication

Allows multiple Agent Zero instances to coordinate.

---

## Troubleshooting

### Common Issues

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| Cannot connect WebSocket | Container not running or port conflict | `docker-compose ps`, check ports, restart |
| LLM returns errors | Invalid API key or model name | Verify credentials, check provider docs for correct model ID format |
| Context window exceeded | Too much chat history | Reduce `Context Window Space` setting, clear chat |
| Speech not working | Missing Whisper model | Check logs, ensure PyTorch installed |
| Tools failing | Permission issues or dependencies | Check container has required packages (apt-get install) |
| Memory not retrieving | Embedding model misconfigured | Test embedding connectivity, check model availability |
| Browser automation fails | Xvfb/display issues | Ensure headless browser dependencies installed |

### Logs

Access logs:
```bash
# Container logs
docker logs -f agent-zero

# HTML session logs (auto-saved)
ls logs/
open logs/<timestamp>_*.html
```

### Debug Mode

Enable verbose logging in settings or via environment:
```bash
A0_SET_debug=true
```

### Support Resources

- [Installation Guide](./docs/setup/installation.md)
- [Usage Guide](./docs/guides/usage.md)
- [Troubleshooting Guide](./docs/guides/troubleshooting.md)
- [Developer Docs](./docs/developer/)
- [Community/Repository Issues](https://github.com/your-repo/issues)

---

## Reference Materials

### Settings Configuration Reference

| Setting | Type | Description | Example |
|---------|------|-------------|---------|
| `llm_provider` | string | Model provider | `anthropic`, `openai`, `openrouter`, `ollama` |
| `llm_model` | string | Model ID | `claude-sonnet-4-5`, `gpt-4o` |
| `context_length` | int | Max tokens | `100000` |
| `context_window_space` | float | Portion for history | `0.5` (50%) |
| `api_key` | string | API key for provider | `sk-...` |
| `ui_login` / `ui_password` | string | Web UI credentials | `admin` |

### Tool Response Format

Tools must return valid JSON matching their schema. Errors should be caught and reported in `error` field if applicable.

### File Naming Conventions

- No spaces in filenames (use hyphens or underscores)
- Use lowercase for consistency
- Project files: `/usr/projects/<name>/`
- Temporary files: `/a0/tmp/` or `/tmp/`

---

## Appendix

### Version History

- **v0.9.8.1**: Model settings: stepfun/step-3.5-flash:free for chat/util, sentence-transformers for embedding
- **v0.9.8**: Skills system introduced, UI redesign, Git projects support
- **v0.9.7**: Agent-specific prompts in `/a0/agents/<agent_name>/prompts/`
- Pre-v0.9.7: Shared `/prompts` directory

### License

See repository LICENSE file.

### Contributing

See [Contribution Guide](./docs/guides/contribution.md).

---

**End of Technical Documentation**
