
## Stage 3B – Token & Cost Telemetry (New)

clone now tracks per-agent token usage and estimated costs in real-time, providing instant insight into LLM spend across your swarm.

### Features

- **LiteLLM integration**: Uses LiteLLM's dynamic pricing database to compute costs for any supported model (OpenAI, Anthropic, OpenRouter, etc.). No manual price updates needed.
- **Clone-level breakdown**: Each clone reports its own token counts and costs to the leader, enabling cost attribution by task or role.
- **Prometheus metrics**: Exposes `a0_tokens_total` (counter) and `a0_cost_total` (gauge) with labels `a0_clone`, `a0_model`, `direction`, `currency`.
- **JSON endpoint**: `GET /token_metrics` returns aggregated counters and costs by clone.
- **Non-blocking recording**: Token telemetry is recorded in the LLM callback without impacting response time.

### Activation

Token telemetry is automatically enabled when `enable_observability: True` is set. No additional setup required.

Ensure LiteLLM is installed: `pip install litellm` (recommended for accurate cost data). If LiteLLM is not available, token counts are still recorded but costs default to $0.

### Streaming Responses

If using streaming LLM responses, the system will attempt to capture token usage from the final chunk when `stream_options={'include_usage': True}` is passed to `litellm.completion`. For models that do not return usage in stream, a fallback token counter may be used in future.

### API Endpoints

- `GET /metrics` – Prometheus-format metrics including token counts and costs.
- `GET /token_metrics` – JSON breakdown by clone and model, e.g.:
  ```json
  {
    "leader": {
      "counters": {"openai/gpt-4o": {"input": 1500, "output": 750}},
      "costs": {"openai/gpt-4o": 0.01875}
    },
    "clone-researcher": {
      "counters": {"anthropic/claude-3-5-sonnet": {"input": 2000, "output": 1000}},
      "costs": {"anthropic/claude-3-5-sonnet": 0.045}
    }
  }
  ```

### Implementation Notes

- The `TokenCounter` singleton collects tokens per clone. Clones send their local token metrics to the leader via the existing `/metrics/containers` endpoint.
- The leader aggregates all counters and emits combined Prometheus lines and the `/token_metrics` JSON.
- Cost computation uses `litellm.model_cost` dictionary, ensuring up-to-date pricing across providers.

---
