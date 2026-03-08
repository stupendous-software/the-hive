---
title: The Hive – An Agent Zero Extension
search: false
---

# The Hive – An Agent Zero Extension 🤖

[![GitHub stars](https://img.shields.io/github/stars/stupendous-software/the-hive?style=social)](https://github.com/stupendous-software/the-hive/stargazers)
[![GitHub watchers](https://img.shields.io/github/watchers/stupendous-software/the-hive?style=social)](https://github.com/stupendous-software/the-hive/watchers)
[![GitHub commits since latest release](https://img.shields.io/github/commit-activity/m/stupendous-software/the-hive)](https://github.com/stupendous-software/the-hive/pulse)

> **The Hive** extends **Agent Zero** to create autonomous AI assistants that remember, collaborate, and get smarter over time. Deploy with one command, customize prompts, and scale with multi‑agent swarms.

---

## 🚀 Try It Now

```bash
docker run -p 50080:80 \
  -v a0_data:/a0/usr \
  -v a0_logs:/a0/logs \
  -v a0_tmp:/a0/tmp \
  -e A0_SET_chat_model_provider=openrouter \
  -e A0_SET_chat_model_name=openrouter/auto \
  agent0ai/agent-zero:latest
```
Then open [http://localhost:50080](http://localhost:50080) and say:

> *"Hey Agent, find recent AI news, summarize, and save the links to memory."

---

## ✨ Why The Hive?

- **🧠 Persistent Memory** – Never repeat yourself; the agent learns your preferences.
- **👥 Multi‑Agent Swarms** – Delegate complex tasks to specialized subordinates (researcher, coder, hacker) and get consolidated answers.
- **🔧 Extensible Skills** – Add new capabilities from a marketplace or build your own.
- **📊 Real‑Time Observability** – Live logs, metrics, and health endpoints.
- **🔐 Secure Secrets** – Credentials are injected safely; never exposed in logs.
- **🌐 Remote Access** – Built‑in tunnels and WebSocket UI.
- **🗣️ Voice Ready** – Text‑to‑Speech (Kokoro) and Speech‑to‑Text (Whisper).

---

## 💡 What You Can Build

- 📚 **Research Assistant** – Automated search, summarization, memory.
- 👨‍💻 **Code Review Bot** – Delegates to `coder`; runs tests, reports.
- 📈 **Ops Monitor** – Scheduled checks, alerts, ticketing.
- 🎓 **Learning Tutor** – Explanations adapt to your level.
- 💰 **Financial Analyst** – Data pulls, charts, correlations.

---

## 📖 Documentation

| Topic | Link |
|-------|------|
| Installation & Setup | [installation.md](./setup/installation.md) |
| Usage Guide | [usage.md](./guides/usage.md) |
| Projects | [projects.md](./guides/projects.md) |
| Skills | [skills.md](./guides/skills.md) |
| API Integration | [api-integration.md](./guides/api-integration.md) |
| MCP & A2A | [connectivity.md](./developer/connectivity.md) |
| Development | [dev-setup.md](./setup/dev-setup.md) |
| Troubleshooting | [troubleshooting.md](./guides/troubleshooting.md) |
| Contributing | [contribution.md](./guides/contribution.md) |

---

## 🆚 How It Compares

| Feature | The Hive | AutoGPT | CrewAI |
|---------|----------|---------|--------|
| Persistent Memory | ✅ | ❌ | Limited |
| Multi‑Agent Swarms | ✅ | ❌ | ✅ |
| Skill Marketplace | ✅ | ❌ | ❌ |
| Observability UI | ✅ | Limited | Varies |
| Docker Deployment | ✅ | ✅ | ✅ |
| Custom Prompts | Full control | Guided | Role‑based |

---

## 📸 Screenshots

![Web UI](/docs/res/usage/web-ui.png)
*Interactive Web UI*

---

## 🤝 Get Involved

- Read the full [docs](./) to get started
- **Contribute**: Check [contribution.md](./guides/contribution.md)
- **Issues**: Report bugs and request features on GitHub

---

> **Ready to build your own hive?** Dive into the documentation and start creating.
