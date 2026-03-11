import json
import time
from datetime import datetime, timezone
from collections import defaultdict

class StructuredLogger:
    def __init__(self, agent_id=None, task_id=None, log_file=None):
        self.agent_id = agent_id or 'unknown'
        self.task_id = task_id or 'unknown'
        self.log_file = log_file
    def _emit(self, record):
        if self.log_file:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(record) + '\n')
        else:
            print(json.dumps(record))
    def log(self, level, message, **extra):
        record = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'agent_id': self.agent_id,
            'task_id': self.task_id,
            'level': level,
            'message': message,
            **extra
        }
        self._emit(record)
    def info(self, message, **extra): self.log('info', message, **extra)
    def warning(self, message, **extra): self.log('warning', message, **extra)
    def error(self, message, **extra): self.log('error', message, **extra)
    def debug(self, message, **extra): self.log('debug', message, **extra)

class MetricsCollector:
    def __init__(self):
        self.counters = defaultdict(int)
        self.gauges = {}
        self.histograms = defaultdict(list)
    def inc(self, name, value=1, tags=None):
        key = name
        if tags:
            key = f"{name}:{':'.join(f'{k}={v}' for k, v in sorted(tags.items()))}"
        self.counters[key] += value
    def gauge(self, name, value, tags=None):
        key = name
        if tags:
            key = f"{name}:{':'.join(f'{k}={v}' for k, v in sorted(tags.items()))}"
        self.gauges[key] = value
    def timing(self, name, milliseconds, tags=None):
        key = name
        if tags:
            key = f"{name}:{':'.join(f'{k}={v}' for k, v in sorted(tags.items()))}"
        self.histograms[key].append(milliseconds)
    def to_dict(self):
        return {
            'counters': dict(self.counters),
            'gauges': dict(self.gauges),
            'histograms': {k: list(v) for k, v in self.histograms.items()}
        }

def get_agent_status():
    from agent import AgentContext
    contexts = getattr(AgentContext, '_contexts', {})
    now = time.time()
    agents = {}
    total_mem = 0
    for ctx in contexts.values():
        try:
            agent_name = getattr(ctx.config, 'agent_name', 'unknown')
            created_at = getattr(ctx, 'created_at', now)
            last_msg = getattr(ctx, 'last_message_time', None)
            paused = getattr(ctx, 'paused', False)
            task_alive = getattr(ctx, 'task_alive', False)
            state = 'running' if task_alive else ('paused' if paused else 'idle')
            agents[ctx.id] = {
                'agent_name': agent_name,
                'context_id': ctx.id,
                'state': state,
                'created_at': created_at,
                'last_message': last_msg,
                'paused': paused,
                'task_alive': task_alive,
            }
            if hasattr(ctx, 'memory') and hasattr(ctx.memory, 'size'):
                try:
                    total_mem += ctx.memory.size()
                except Exception: pass
        except Exception: continue
    active = sum(1 for a in agents.values() if a['state'] == 'running')
    idle = sum(1 for a in agents.values() if a['state'] == 'idle')
    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'agents': agents,
        'summary': {
            'active_agents': active,
            'idle_agents': idle,
            'total_agents': len(agents),
            'avg_memory_entries': total_mem / max(1, len(agents)),
        },
        'metrics': MetricsCollector().to_dict(),
    }
