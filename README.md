<div align="center">

# `Agent Zero`

<p align="center">
    <a href="https://trendshift.io/repositories/11745" target="_blank"><img src="https://trendshift.io/api/badge/repositories/11745" alt="frdel%2Fagent-zero | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>
</p>

[![Agent Zero Website](https://img.shields.io/badge/Website-agent--zero.ai-0A192F?style=for-the-badge&logo=vercel&logoColor=white)](https://agent-zero.ai) [![Thanks to Sponsors](https://img.shields.io/badge/GitHub%20Sponsors-Thanks%20to%20Sponsors-FF69B4?style=for-the-badge&logo=githubsponsors&logoColor=white)](https://github.com/sponsors/agent0ai) [![Follow on X](https://img.shields.io/badge/X-Follow-000000?style=for-the-badge&logo=x&logoColor=white)](https://x.com/Agent0ai) [![Join our Discord](https://img.shields.io/badge/Discord-Join%20our%20server-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/B8KZKNsPpj) [![Subscribe on YouTube](https://img.shields.io/badge/YouTube-Subscribe-red?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@AgentZeroFW) [![Connect on LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/jan-tomasek/) [![Follow on Warpcast](https://img.shields.io/badge/Warpcast-Follow-5A32F3?style=for-the-badge)](https://warpcast.com/agent-zero)

</div>

---

## 🐝 The Hive: Multi-Agent Orchestration for Agent Zero

> **Agent Zero** is a personal, organic agentic framework that grows and learns with you. This fork extends it with **Hive capabilities** — enabling you to run, manage, and monitor swarms of autonomous agents.

### ✨ What's New in This Fork

- **Comprehensive Documentation**
  - 📘 [Technical Documentation](./docs/Technical_Documentation.md) — 19KB, 13-section deep dive
  - 🚀 [Quickstart Guide](./docs/guides/Quickstart_Guide.md) — get running in 5 minutes

- **New Skills for the Hive**
  - `agent-clone` — spawn new Agent Zero Docker instances with isolated memory
  - `clone-heartbeat-monitor` — health checks and heartbeat tracking
  - `clone-manager` — full lifecycle management of the agent swarm
  - `smtp-email-sender` — notifications for hive events

- **Enhanced Ecosystem**
  - Git-based Projects with authentication for public/private repositories
  - Project isolation structures for multi-client support
  - Core updates: health, history, settings, TTY session handling

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [Quickstart Guide](./docs/guides/Quickstart_Guide.md) | 5‑minute setup, example prompts, pro tips |
| [Technical Documentation](./docs/Technical_Documentation.md) | Complete reference: architecture, configuration, tools, security, troubleshooting |
| [Usage Guide](./docs/guides/usage.md) | How to use Agent Zero day‑to‑day |
| [Projects Tutorial](./docs/guides/projects.md) | Multi‑client project isolation |

---

## ⚡ Quick Start

### Prerequisites
- Docker & Docker Compose
- 4GB+ RAM (8GB recommended)
- Internet connection (for cloud LLMs)

### One‑Line Bootstrap

```bash
docker-compose up -d
```

Then open **http://localhost:8080** and configure your LLM provider (Anthropic, OpenAI, OpenRouter, Ollama, etc.) in Settings.

### Docker Run (Alternative)

```bash
docker pull agent0ai/agent-zero
docker run -p 50001:80 agent0ai/agent-zero
# Visit http://localhost:50001
```

> **📺 Watch** the installation video: [Easy Installation guide](https://www.youtube.com/watch?v=w5v5Kjx51hs)

---

## 🧠 Key Features

1. **General‑purpose Assistant**
   - Not pre‑programmed for specific tasks; grows organically with you.
   - Persistent memory remembers solutions, code, facts, and instructions.

2. **Computer as a Tool**
   - Writes its own code, uses the terminal, creates tools on the fly.
   - Default tools: online search, memory, communication, code/terminal execution.

3. **Multi‑agent Cooperation (The Hive)**
   - Every agent can spawn subordinates and report to a superior.
   - This fork adds dedicated skills to **clone**, **monitor**, and **manage** swarms of agents.
   - Project isolation keeps different clients/tasks separated.

4. **Completely Customizable**
   - Nothing is hard‑coded. Behavior is defined by prompts in `/a0/agents/<name>/prompts/`.
   - Extend via **Skills** (SKILL.md standard) — compatible with Claude Code, Cursor, Copilot, etc.

---

## 🔧 New Skills (Hive Management)

### `agent-clone`
Spawn a new Agent Zero Docker container with its own memory and context. Use this to scale your hive.

### `clone-heartbeat-monitor`
Periodically check that all cloned agents are alive and responding. Configure alerts.

### `clone-manager`
Manage the lifecycle of your agents: start, stop, update, and clean up clones.

### `smtp-email-sender`
Send email notifications for important hive events (agent down, task completed, etc.).

See each skill's `SKILL.md` for detailed usage.

---

## 🛠️ Development & Extensibility

- **Custom Tools**: Create your own tools in `tools/` and register them.
- **Skills**: Portable, structured capabilities using the open `SKILL.md` standard.
- **Projects**: Git‑based projects with authentication; clone codebases directly into isolated workspaces.
- **Scheduler**: Cron‑based, planned, and adhoc tasks.
- **Settings**: Web UI with fine‑grained control over LLMs, embeddings, speech, security, and more.

---

## 🔐 Security Notes

- Agent Zero runs with full privileges inside its container. Only run trusted code.
- Use **Project Isolation** to separate different clients or tasks.
- Never paste secrets into chat; use project secrets or environment variables.
- Enable UI authentication in Settings.

---

## 📦 Version Highlights (This Fork)

- **v0.9.8+** Skills system, clone management, heartbeat monitoring, SMTP notifications, Hive documentation.

Original project version history (abbreviated):

- v0.9.8 — Skills, UI redesign, Git projects
- v0.9.7 — Projects management
- v0.9.6 — Memory Dashboard
- v0.8 — Docker runtime, TTS/STT, browser agent, multitasking

---

## 🤝 Community & Support
- [Follow our YouTube channel](https://www.youtube.com/@AgentZeroFW) for tutorials.
- [Report Issues](https://github.com/stupendous-software/skynet/issues) for this fork.
- Upstream: [agent0ai/agent-zero](https://github.com/agent0ai/agent-zero)

---

## 📄 License

[See LICENSE file](./LICENSE) — inherits from upstream Agent Zero.

---

<sup>This README is tailored for the **Hive Improvements** fork, focusing on multi-agent orchestration and ecosystem skills. For the complete reference, see [Technical Documentation](./docs/Technical_Documentation.md).</sup>
