# Architecture Overview

Core components:
- AgentContext: manages contexts and agent lifecycle.
- StructuredLogger: JSON logging.
- MetricsCollector: runtime metrics.
- Status API: FastAPI endpoints.
- Subordinate orchestration via call_subordinate tool.
- Skills loading system.
- Memory backend with AI recall.
