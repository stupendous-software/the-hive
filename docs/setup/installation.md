# Installation Guide

clone (The Hive) is designed for Docker deployment (recommended) but also supports manual installation.

## Prerequisites

- Docker 20.10+ (recommended) or Python 3.11+ (for manual)
- 2GB+ RAM (4GB+ recommended)
- 10GB+ disk space (depends on models and data)
- Git (optional, for source deployment)

## Docker Deployment (Recommended)

### Pull the Image

```bash
docker pull agent0ai/agent-zero:latest
```

For production stability, consider using a dated tag (e.g., `agent0ai/agent-zero:0.9.8`).

### Run the Container

```bash
docker run -d \
  --name agent-zero \
  -p 50080:80 \
  -p 8080:8080 \
  -v a0_usr:/a0/usr \
  -v a0_logs:/a0/logs \
  -e A0_OBSERVABILITY_PORT=8080 \
  -e A0_SET_chat_model_provider=openrouter \
  -e A0_SET_chat_model_name=openrouter/auto \
  agent0ai/agent-zero:latest
```

**Explanation:**
- `-p 50080:80` – Web UI
- `-p 8080:8080` – Status API (health, metrics)
- `-v a0_usr:/a0/usr` – Persistent data (memory, projects, secrets)
- `-v a0_logs:/a0/logs` – Logs and HTML logs
- `-e A0_SET_...` – Automatic configuration (see [Advanced Configuration](#advanced-configuration))

After startup, open `http://localhost:50080` in your browser.

### Advanced Configuration via Environment Variables

You can configure many clone settings without manual UI steps using the `A0_SET_` prefix. This enables automated deployments.

**Usage:**

Add variables to your `.env` file or Docker `-e` flags:

```env
# Model configuration
A0_SET_chat_model_provider=anthropic
A0_SET_chat_model_name=claude-3-5-sonnet-20241022
A0_SET_chat_model_ctx_length=200000

# Memory settings
A0_SET_memory_recall_enabled=true
A0_SET_memory_recall_interval=5

# Agent configuration
A0_SET_agent_profile=custom
A0_SET_agent_memory_subdir=production
```

These provide initial defaults when `settings.json` does not override them. Once a value is saved via the UI, it takes precedence. For a complete list, see `settings.json` after first run.

**Docker example:**

```bash
docker run -d \
  -p 50080:80 \
  -v a0_usr:/a0/usr \
  -e A0_SET_chat_model_provider=anthropic \
  -e A0_SET_chat_model_name=claude-3-5-sonnet-20241022 \
  agent0ai/agent-zero:latest
```

**Notes:**
- Sensitive credentials (API keys) should still be provided as their native environment variables (e.g., `OPENROUTER_API_KEY`) or via a mounted secret volume.
- Container/process restart required for changes to take effect if the value is only read at startup.

### Secret Management

clone requires API keys for LLM providers and other services. Use Docker secrets or a mounted volume – never bake them into images.

```bash
docker run -d \
  ... \
  -v hive_secrets:/a0/usr/.secrets \
  agent0ai/agent-zero:latest
```

Inside `/a0/usr/.secrets`, create files named as the expected environment variable (e.g., `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`). The agent reads them securely and does not expose raw values in logs.

### Observability Port

The status API listens on port `8080` by default. Change it with `A0_OBSERVABILITY_PORT`:

```bash
docker run -d \
  -p 9090:9090 \
  -e A0_OBSERVABILITY_PORT=9090 \
  ...
```

Then health check: `http://localhost:9090/health`.

### Production Docker Compose Example

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  agent-zero:
    image: agent0ai/agent-zero:0.9.8
    container_name: agent-zero
    restart: unless-stopped
    ports:
      - "50080:80"
      - "9090:9090"
    volumes:
      - a0_usr:/a0/usr
      - a0_logs:/a0/logs
      - hive_secrets:/a0/usr/.secrets
      - ./providers.yaml:/a0/usr/providers.yaml:ro
    environment:
      - A0_OBSERVABILITY_PORT=9090
      - A0_SET_chat_model_provider=anthropic
      - A0_SET_chat_model_name=claude-3-5-sonnet-20241022
      - A0_SET_memory_recall_enabled=true
      - A0_SET_memory_recall_interval=5

volumes:
  a0_usr:
  a0_logs:
  hive_secrets:
```

Run: `docker-compose up -d`.

## Manual Setup

For development or custom deployments.

### Clone and Install

```bash
git clone https://github.com/agent0ai/agent-zero.git
cd agent-zero
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r a0/requirements.txt
```

### Configuration

- Create a `.env` file with your API keys (e.g., `OPENROUTER_API_KEY=sk-...`).
- Optionally create `a0/usr/settings.json` to override defaults.
- Place `providers.yaml` (if needed) in `a0/usr/`.

### Run

```bash
python a0/agent.py
```

Web UI: `http://localhost:50080`. Status API: `http://localhost:8080/health`.

## Development Setup

See [Development Setup](./dev-setup.md) for core development.

## VPS Deployment

See [VPS Deployment Guide](./vps-deployment.md) for production hardening, Nginx, SSL, and firewall.

## Remote Access via Tunneling

If you need external access without opening ports, use the built-in tunnel feature (Settings → Tunnel) or see the usage guide: [Remote Access via Tunneling](./usage.md#remote-access-via-tunneling).

## Troubleshooting

Check the [Troubleshooting Guide](./troubleshooting.md) for common issues.

---

**Note:** Keep your container image or repository updated. Backup `a0/usr/` regularly.
