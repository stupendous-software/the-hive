# Agent Zero 🤖
![Version](https://img.shields.io/badge/version-0.9.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-yellow.svg)

> **The Hive: A personal, organic AI agent that grows with you.**

Agent Zero (The Hive) is a production-ready, multi-agent framework for building autonomous AI assistants that learn, remember, and collaborate. Designed for developers, researchers, and power users, it provides a secure, observable, and extensible platform for deploying AI agents that work for you.

---

## ✨ Why Agent Zero?

- **🧠 Persistent Memory** – Agents remember across sessions, with AI-powered recall and consolidation.
- **👥 Multi-Agent Swarms** – Spawn subordinate agents with dedicated prompts, tools, and roles via `call_subordinate`.
- **🔧 Extensible Skills System** – Install skills from a marketplace or create your own to extend capabilities.
- **🛠️ Rich Toolset** – Browser automation, code execution, file handling, webhooks, scheduler, and MCP/A2A protocols.
- **📊 Real-Time Observability** – Structured logs, metrics, health endpoints, and WebSocket UI for live monitoring.
- **🔐 Secrets Management** – Credentials are injected securely; agents never expose raw secrets.
- **🌐 Remote Access** – Built-in tunnel support, WebSocket server, and mobile-friendly UI.
- **📁 Project Isolation** – Multiple projects with separate memory, instructions, and secrets.
- **🗣️ Speech Integration** – Text-to-Speech (Kokoro) and Speech-to-Text (Whisper) support.
- **🐳 Docker Native** – One-command Docker deployment with auto-recovery and volume layering.

---

## 🚀 Quick Example

Below is a minimal script showing how to create an agent, use tools, and delegate to a subordinate.

```python
from python.api.agents import AgentContext
from python.helpers import files, log

# 1. Create a context and agent
ctx = AgentContext(
    config=None,
    name="demo",
    set_current=True
)
agent = ctx.agent0

# 2. Run a task (simple query)
response = agent.run("Calculate 2 + 2 and explain the result.")
print("Agent response:", response)

# 3. Save something to memory
agent.memory_save("User prefers concise answers.")

# 4. Spawn a subordinate for a specialized task
sub_response = agent.call_subordinate(
    profile="researcher",
    message="Find the latest AI news and summarize."
)
print("Subordinate response:", sub_response)
```

---

## 📦 Installation

### Docker (Recommended)

```bash
docker run -p 50080:80 \
  -v a0_usr:/a0/usr \
  -v a0_logs:/a0/logs \
  -e A0_SET_chat_model_provider=openrouter \
  -e A0_SET_chat_model_name=openrouter/auto \
  agent0ai/agent-zero:latest
```

Then open `http://localhost:50080`.

### Manual Setup

```bash
# Clone
$ git clone https://github.com/agent0ai/agent-zero.git
$ cd agent-zero

# Virtual env
$ python -m venv venv
$ source venv/bin/activate  # Windows: venv\\Scripts\\activate

# Install
$ pip install -r a0/requirements.txt

# Run
$ python a0/agent.py
```

---

## 🧭 Core Features in Depth

### Multi-Agent & Subordinates
- Agent Zero can spawn subordinate agents on-demand with different prompt profiles (e.g., `coder`, `researcher`, `hacker`).
- Each subordinate has its own memory, tools, and context, enabling parallel task execution.
- Built-in delegation: the parent agent orchestrates tasks and aggregates results.

### Skills & Extensibility
- Skills are self-contained packages (following SKILL.md standard) that add new tools, commands, or UI components.
- Install from the skill marketplace or develop locally.
- Skills can include scripts, documentation, and prompts.

### Observability & Debugging
- **Status API**: `GET /status`, `GET /metrics`, `GET /health` expose runtime health.
- **Structured Logging**: All tool calls and LLM interactions are logged in JSON format.
- **WebSocket Live Feed**: UI streams logs, messages, and metrics in real-time.
- **Debug Decorators**: `@log_tool_call`, `@log_llm_prompt` for fine-grained instrumentation.

### Memory & Knowledge
- AI-powered memory recall: episodic and semantic storage.
- Consolidation: memories are periodically summarized.
- Configurable recall intervals and embedding models.
- Export/import for backup and migration.

### Security & Compliance
- Secrets management: API keys and credentials stored in a secure volume; agents access them via placeholders.
- No raw secrets in logs or context.
- Role-based isolation via projects.

### Connectivity & Protocols
- **MCP Server/Client**: Agent Zero can act as an MCP server or connect to external MCP servers.
- **A2A (Agent-to-Agent)**: FastA2A protocol for secure inter-agent communication.
- **Scheduler & Wait**: Plan tasks, use `wait` tool for delays or timed execution.
- **Webhooks**: Trigger external actions on events.

---

## 📚 Documentation

Our documentation is structured for quick onboarding and deep dives:

| Topic | Link |
|-------|------|
| Installation & Setup | [docs/setup/installation.md](./docs/setup/installation.md) |
| Usage Guide | [docs/guides/usage.md](./docs/guides/usage.md) |
| Projects | [docs/guides/projects.md](./docs/guides/projects.md) |
| Skills | [docs/guides/skills.md](./docs/guides/skills.md) |
| API Integration | [docs/guides/api-integration.md](./docs/guides/api-integration.md) |
| MCP & A2A | [docs/developer/connectivity.md](./docs/developer/connectivity.md) |
| Development | [docs/setup/dev-setup.md](./docs/setup/dev-setup.md) |
| Troubleshooting | [docs/guides/troubleshooting.md](./docs/guides/troubleshooting.md) |

---

## 🤝 Contributing

We welcome contributions! Please read our [Contribution Guide](./docs/guides/contribution.md) before submitting PRs.

Key areas:
- Bug fixes and stability improvements
- New skills and tools
- Documentation and translations
- UI/UX enhancements

---

## 🙏 Community

- **Discord**: [Join us](https://discord.gg/B8KZKNsPpj)
- **Skool**: [agent-zero.com](https://www.skool.com/agent-zero)
- **YouTube**: [Channel](https://www.youtube.com/@AgentZeroFW)

---

## 📜 License

MIT – see [LICENSE](./LICENSE) for details.

---

> **Built with modern Python, FastAPI, LangChain LiteLLM, Playwright, and more.**
> 
> *The agent that grows with you.*
