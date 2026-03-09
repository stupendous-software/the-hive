# The Hive – An Agent Zero Extension 🤖

[![GitHub stars](https://img.shields.io/github/stars/stupendous-software/the-hive?style=social)](https://github.com/stupendous-software/the-hive/stargazers)
[![GitHub watchers](https://img.shields.io/github/watchers/stupendous-software/the-hive?style=social)](https://github.com/stupendous-software/the-hive/watchers)
[![GitHub commits since latest release](https://img.shields.io/github/commit-activity/m/stupendous-software/the-hive)](https://github.com/stupendous-software/the-hive/pulse)

![Version](https://img.shields.io/badge/version-0.9.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-yellow.svg)

> **The Hive** extends **Agent Zero** with advanced multi‑agent swarms, persistent memory, and observability. It’s a production‑ready platform for building autonomous AI assistants that remember, collaborate, and grow with you.

---

## ✨ Why choose The Hive?

- **🧠 Persistent Memory** – Your agent recalls past conversations and learns your preferences, so you never repeat yourself.
- **👥 Multi‑Agent Swarms** – Delegate complex tasks to specialized sub‑agents (researcher, coder, hacker) and get consolidated answers.
- **🔧 Extensible Skills** – Install community skills or build your own to add new capabilities in minutes.
- **📊 Real‑Time Observability** – Watch agent behavior with live logs, metrics, and health endpoints (no black‑box AI).
- **🔐 Secrets Management** – API keys and credentials are injected securely; agents never expose raw secrets.
- **🌐 Remote Access** – Built‑in tunnel support, WebSocket server, and a mobile‑friendly UI.
- **📁 Project Isolation** – Multiple projects with separate memory, instructions, and secrets.
- **🗣️ Speech Integration** – Text‑to‑Speech (Kokoro) and Speech‑to‑Text (Whisper) support.
- **🐳 Docker Native** – One‑command Docker deployment with auto‑recovery and volume layering.

---

## 🚀 Get Started in 60 Seconds

### Prerequisites
- Docker (recommended) **or** Python 3.11+
- An LLM provider API key (OpenRouter, OpenAI, Anthropic, etc.)

### One‑Command Launch
```bash
docker run -p 50080:80 \
  -v a0_data:/a0/usr \
  -v a0_logs:/a0/logs \
  -v a0_tmp:/a0/tmp \
  -e A0_SET_chat_model_provider=openrouter \
  -e A0_SET_chat_model_name=openrouter/auto \
  brianheston/the-hive:latest
```
Then open `http://localhost:50080` and say:

> *"Hey Agent, find recent AI news, summarize, and save the links to memory."

The agent will spawn a subordinate researcher, fetch the data, and remember the result for later.

---

## 📖 Core Concepts in a Nutshell

1. **Computer as a Tool** – Agent Zero uses your operating system as a tool. It can write code and use the terminal to create and run its own tools on the fly.
2. **Multi‑Agent Cooperation** – Every agent can spawn subordinates. Superiors delegate subtasks and aggregate results; the chain ends with the human user.
3. **Completely Customizable** – Nothing is hard-coded. Change the system prompt, tools, or messages in the `prompts/` folder to reshape behavior.
4. **Communication is Key** – Instruct your agents in natural language. The terminal UI streams responses in real time; you can intervene anytime.

![Multi-agent architecture](docs/res/usage/multi-agent.png)

---

## 💡 Real‑World Use Cases

| What you can build | How The Hive helps |
|-------------------|-------------------|
| Personal research assistant | Automated web search, summarization, memory |
| Code review bot | Delegates to `coder` subordinate, runs tests, reports results |
| Ops monitoring | Scheduled checks, alerts, ticket creation |
| Learning tutor | Adapts explanations to your level over time |
| Financial analysis | Pull market data, generate charts, correlate events |
| API integration without code | Learn and remember integrations from snippets |

---

## 🛠️ Installation & Setup

### Docker (Recommended)
```bash
docker run -p 50080:80 \
  -v a0_data:/a0/usr \
  -v a0_logs:/a0/logs \
  -v a0_tmp:/a0/tmp \
  -e A0_SET_chat_model_provider=openrouter \
  -e A0_SET_chat_model_name=openrouter/auto \
  brianheston/the-hive:latest
```

### Manual Setup
```bash
# Clone the repository
git clone https://github.com/brianheston/the-hive.git
cd agent-zero

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r a0/requirements.txt

# Run the agent
python a0/agent.py
```

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

**Docs landing page**: [docs/index.md](./docs/index.md)

---

## 🙌 Contributing

We welcome contributions! Please read our [Contribution Guide](./docs/guides/contribution.md) before submitting PRs.

Key areas:
- Bug fixes and stability improvements
- New skills and tools
- Documentation and translations
- UI/UX enhancements

---

## ⚠️ Keep in Mind

1. **The Hive can be powerful** – With proper instruction, it can perform many actions on your computer. Always run it in an isolated environment (like Docker) and be careful what you ask for.
2. **Prompt‑based framework** – The entire behavior is defined by prompts in the `prompts/` folder. Change them to dramatically alter functionality.

---

## 📜 License

MIT – see [LICENSE](./LICENSE) for details.

---

> Built with modern Python, FastAPI, LiteLLM, Playwright, and more.
> 
> *The agent that grows with you.*
