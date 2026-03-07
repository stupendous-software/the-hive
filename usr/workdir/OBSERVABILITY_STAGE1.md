# Observability Stage 1 – Quick Wins

## Components Added
- `observability/`: structured logger, metrics collector, system status
- `status_api.py`: FastAPI app exposing `/status`, `/metrics`, `/health`
- `a0_status`: CLI command to print agent status JSON
- `observability/debug.py`: decorators to wrap tools and LLM calls for debug logging

## How to Integrate
1. In your agent runtime, import the logger: `from observability import StructuredLogger` and create an instance per agent.
2. Wrap tool functions with `@log_tool_call(logger)` from `debug.py` to auto-log duration and arguments.
3. For LLM calls, wrap the prompt function with `@log_llm_prompt(logger)`.
4. Start the status API server: `python status_api.py &` or integrate into main process.
5. Access: `http://localhost:8080/status` and `/metrics` (Port configurable via `A0_OBSERVABILITY_PORT`).
6. CLI: `./a0_status` prints current status.

## Dependencies
Added to requirements.txt: fastapi, uvicorn, psutil, structlog.

## Next Steps (Stage 2)
- Implement real agent/task enumeration in `get_agent_status()`
- Wire metrics into the MetricsCollector and expose Prometheus format
- Add debug mode toggle via environment to emit full prompts
- Add correlation IDs across tool calls
