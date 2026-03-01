# Agent Zero Framework - Quickstart Guide

## 🚀 Get Started in 5 Minutes

This guide will get you up and running with Agent Zero, your AI assistant that can execute tasks autonomously using tools.

---

## 📋 Prerequisites

- Docker & Docker Compose installed
- 4GB+ RAM (8GB recommended)
- Internet connection (for cloud LLMs)

---

## ⚡ Quick Installation

### 1. Clone & Setup

```bash
# Clone the repository (or extract your copy)
git clone <your-repo-url>
cd agent-zero

# Optional: Configure environment
cp .env.example .env
# Edit .env if you want custom ports or settings
```

### 2. Start the Container

```bash
docker-compose up -d
```

This starts:
- WebSocket server on port 3000
- Web UI on port 8080

### 3. Access the Interface

Open your browser to: **http://localhost:8080**

You should see the Agent Zero Web UI.

---

## 🔑 Initial Configuration

### Configure Your LLM (5 minutes)

1. Click **Settings** in the Web UI
2. Scroll to **Chat Model Settings**
3. Choose your provider:
   - **Anthropic** → Claude models
   - **OpenAI** → GPT-4, GPT-4o
   - **OpenRouter** → Many providers & models
   - **Ollama** → Local models (e.g., `llama3`, `mistral`)
   - **OpenAI Compatible** → Custom endpoints
4. Enter your **Model Name** (provider-specific)
5. Add your **API Key** (if required)
6. Click **Save**

> **💡 Tip**: For local models, set API URL to your local endpoint (e.g., Ollama: `http://host.docker.internal:11434/v1`)

### Utility Model (Recommended)

Scroll to **Utility Model Configuration** and set a strong model for memory tasks (70B-class or GPT-4/Claude flash models work best).

---

## 🎯 First Conversation

Once configured, you can start chatting. Try these example prompts:

```
What tools do you have available?
```

```
Create a Python script that calculates fibonacci numbers and save it to /tmp/fib.py
```

```
Search the web for the latest news about AI agents
```

```
Analyze this PDF document and summarize the key points
```
*(attach a PDF file)*

---

## 🏗️ Project Isolation

Agent Zero supports project-based isolation. To use:

1. Create a project in **Projects** panel
2. Activate the project (toggles switch)
3. All files, memory, and secrets are now scoped to that project

**Why?** Prevents context bleed between different clients or work types.

---

## 📁 File Operations

All file operations happen inside the container. Use absolute paths:

- `/a0/usr/workdir/` - Your working directory (not in projects)
- `/usr/projects/<project_name>/work/` - Project-specific files
- `/tmp/` - Temporary files
- `/a0/tmp/` - Agent Zero temp files

> **⚠️ Important**: Don't use spaces in filenames. Use hyphens or underscores.

---

## 🔐 Security Essentials

### What You Should Know

- **Agent Zero has root access** inside the container
- It can execute any command, modify files, make network requests
- **Only run trusted code** and be careful with credentials

### Best Practices

1. **Use project isolation** for different clients
2. **Never paste secrets** into chat (use project secrets in Settings > Projects)
3. **Set UI authentication**: Enable login/password in Settings
4. **Keep Docker isolated** from host network if handling sensitive data
5. **Review tool outputs** before executing destructive operations

---

## 🛠️ Common Tools

### Execute Code

```json
{
  "thoughts": ["I need to run a shell command"],
  "headline": "Running terminal command",
  "tool_name": "code_execution_tool",
  "tool_args": {
    "runtime": "terminal",
    "code": "ls -la /usr/projects"
  }
}
```

### Web Search

```json
{
  "thoughts": ["I need to search the web"],
  "headline": "Searching the web",
  "tool_name": "search_engine",
  "tool_args": {
    "query": "latest Python version"
  }
}
```

### Document Analysis

```json
{
  "thoughts": ["Analyze this PDF"],
  "headline": "Reading document",
  "tool_name": "document_query",
  "tool_args": {
    "document": "file:///path/to/document.pdf",
    "queries": ["What are the main conclusions?"]
  }
}
```

---

## 💾 Memory System

Agent Zero has two memory types:

1. **Conversation Context** - Current chat history
2. **Long-term Memory** - Persistent knowledge (semantic search enabled)

**Save to memory**:
```json
{
  "tool_name": "memory_save",
  "tool_args": {
    "text": "Your important information here"
  }
}
```

**Retrieve from memory**:
```json
{
  "tool_name": "memory_load",
  "tool_args": {
    "query": "your search query",
    "threshold": 0.7,
    "limit": 5
  }
}
```

---

## ⏰ Task Scheduler

Schedule automated tasks that run at specific times or intervals.

**Create a scheduled task** (runs every 30 minutes):

```json
{
  "tool_name": "scheduler:create_scheduled_task",
  "tool_args": {
    "name": "Daily Backup",
    "system_prompt": "You are a backup specialist.",
    "prompt": "Compress all files in /usr/projects/myproject/work/ into a tar.gz and save to /backups/",
    "schedule": {
      "minute": "*/30",
      "hour": "*",
      "day": "*",
      "month": "*",
      "weekday": "*"
    },
    "dedicated_context": true
  }
}
```

**List tasks**:
```json
{
  "tool_name": "scheduler:list_tasks"
}
```

---

## 🔧 Skills System

Skills extend Agent Zero with specialized capabilities.

**List available skills**:
```json
{
  "tool_name": "skills_tool:list"
}
```

**Load a skill** to see its instructions:
```json
{
  "tool_name": "skills_tool:load",
  "tool_args": {
    "skill_name": "smtp-email-sender"
  }
}
```

Then follow the skill's documentation to use it.

---

## 🆘 Troubleshooting

### Cannot connect to WebSocket

```bash
# Check if container is running
docker-compose ps

# Restart if needed
docker-compose restart
```

### LLM returns "Invalid model"

- Double-check the model name format (provider-specific)
- Verify your API key has access to that model

### Context window exceeded

- Reduce **Context Window Space** in Settings
- Or clear chat history and start fresh

### Speech features not working

Check logs for missing dependencies. Install in container:
```bash
docker-compose exec agent-zero apt-get update && apt-get install -y ffmpeg
```

---

## 📚 Where to Go Next

- **Full Technical Documentation**: See `Technical_Documentation.md` in this directory
- **Settings Reference**: Web UI Settings panel (all options documented)
- **Tools Reference**: Available tools listed in system prompts
- **Developer Guide**: `/docs/developer/` in the repository
- **Troubleshooting Guide**: `docs/guides/troubleshooting.md`

---

## 🎓 Key Concepts Recap

1. **Tools** - Agent uses these to take actions (code execution, search, etc.)
2. **Projects** - Isolate work by client/task with separate memory & secrets
3. **Skills** - Modular extensions for specialized tasks
4. **Memory** - Long-term knowledge storage with semantic search
5. **Scheduler** - Automate recurring or planned tasks
6. **Settings** - Configure via Web UI or environment variables

---

## ⚡ Pro Tips

1. **Streaming Output** - Watch responses generate in real-time; interrupt anytime
2. **HTML Logs** - All sessions are auto-saved to `logs/` directory
3. **Include Files** - Use `§§include(/path/to/file)` to include file contents in responses
4. **Don't Rewrite** - Include large outputs rather than retyping them
5. **Use Dark Mode** - Default theme is dark for eye comfort
6. **No Spaces in Filenames** - Use hyphens/underscores
7. **Check Tools Available** - Say "what tools do you have" to see current capabilities

---

## 🎉 You're Ready!

Agent Zero is now running and configured. Start chatting, explore the tools, and build powerful automations.

**Remember**: With great power comes great responsibility. Use wisely.

---

**Need Help?** Check the full Technical Documentation or repository resources.
