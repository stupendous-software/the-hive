from datetime import datetime, timezone


def get_agent_status_simple():
    """Return simple static status when agent contexts are not available."""
    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'agents': {},
        'summary': {'active_agents': 0, 'idle_agents': 0, 'total_agents': 0, 'avg_memory_entries': 0},
        'metrics': {},
        'note': 'Simplified status; real agent data will appear once AgentContext is active.'
    }
