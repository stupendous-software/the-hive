# Troubleshooting

Common issues and solutions for running Agent Zero.

## Web UI Not Loading

**Symptom:** Blank page, connection refused on `localhost:50080`.

**Check:**

- Port conflict: change mappings (`-p 50081:80`).
- Container status: `docker ps` – ensure the container is running.
- Firewall: allow the Web UI port.
- If inside Docker, use `docker exec agent-zero curl http://localhost:80` to verify.

## Status API Unreachable

**Symptom:** `GET /health` fails.

**Solutions:**

- Confirm the observability port matches `A0_OBSERVABILITY_PORT`.
- Test from inside container: `docker exec agent-zero curl http://localhost:8080/health`.
- Check container logs: `docker logs agent-zero`.

## Agent Crashes on Startup

**Possible causes:**

- Invalid `settings.json`. Delete it to regenerate defaults.
- Missing dependencies (manual setup): `pip install -r a0/requirements.txt`.
- Permission issues on volumes: ensure the container can write to mounted directories. On Linux, `sudo chown 1000:1000 /path/to/host/dir` or use named volumes.

## Memory/RAM Exhaustion

**Mitigation:**

- Increase `memory_recall_interval` to recall less frequently.
- Reduce embedding model size if using a custom one.
- Increase host resources or Docker memory limit (`docker run -m 4g ...`).
- Clean up unused projects and memories.

## LLM Provider Connection Failures

**Debug:**

- Verify API key is correct and set as environment variable or secret file.
- Check outbound internet access (for cloud providers).
- For local providers (Ollama), ensure the URL is correct and the service is running and CORS allows.
- Look at logs in `a0/logs/` for detailed error messages.

## Docker Socket Required Errors

Some features (e.g., Docker-in-Docker) need the host Docker socket. Add:

```bash
-v /var/run/docker.sock:/var/run/docker.sock
```

## MCP/A2A Connectivity Issues

- Verify MCP server is enabled in Settings and the port is open.
- For A2A, ensure the shared secret matches on both ends.
- Test with `curl` to the endpoints.

## Slow Responses

- Model may be rate-limited; try a different provider or model.
- Memory recall may be too frequent; increase interval.
- Code execution in sandbox may be slow; optimize scripts or use a faster runtime.

## Logs Not Streaming in UI

- Refresh the browser and ensure WebSocket connection is established.
- Check that `a0_status` shows logging is active.
- Enable debug mode in Settings for more verbose output.

## Post-Upgrade Problems

- Check the Changelog for breaking changes.
- Use Settings → Backup to restore from a previous backup.
- Report issues with logs and version info.

## Getting Help

- [Discord](https://discord.gg/B8KZKNsPpj)
- [Skool](https://www.skool.com/agent-zero)
- [GitHub Issues](https://github.com/agent0ai/agent-zero/issues)
