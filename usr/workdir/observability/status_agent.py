import json
from datetime import datetime, timezone
from pathlib import Path


def get_public_url():
    try:
        settings_path = Path('/a0/usr/settings.json')
        if settings_path.exists():
            settings = json.loads(settings_path.read_text())
            return settings.get('public_url', 'http://localhost')
    except Exception:
        pass
    return 'http://localhost'


def get_agent_status_simple():
    """Return simple static status when agent contexts are not available."""
    base = get_public_url()
    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'agents': {},
        'summary': {
            'active_agents': 0,
            'idle_agents': 0,
            'total_agents': 0,
            'avg_memory_entries': 0
        },
        'metrics': {},
        'note': 'Simplified status; real agent data will appear once AgentContext is active.',
        'dashboard_url': f"{base}/status",
        'health_url': f"{base}/health",
        'metrics_url': f"{base}/metrics"
    }
