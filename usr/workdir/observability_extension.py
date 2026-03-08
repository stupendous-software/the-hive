import os
import sys
sys.path.insert(0, '/a0/usr/workdir')
from python.helpers.extension import register_extension
from observability import StructuredLogger, MetricsCollector
from observability import tracing
import audit  # global audit_logger
from vault import vault as global_vault
from policy import policy_engine as global_policy
import time as _time
import threading
import json
import uuid
from datetime import datetime, timezone

# Optional deps for clone reporting
try:
    import docker
    import requests
    _HAVE_CLONE_DEPS = True
except ImportError:
    _HAVE_CLONE_DEPS = False

_llm_start_times = {}
_obs_server_started = False

# Clone reporting control
_metrics_thread = None
_logs_thread = None
_trace_thread = None
_metrics_stop = threading.Event()
_logs_stop = threading.Event()
_trace_stop = threading.Event()
_trace_spans = []
_trace_lock = threading.Lock()

# Token telemetry integration
from token_telemetry import token_counter


def _calculate_cpu_percent(stats):
    try:
        cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
        system_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
        if system_delta > 0:
            return (cpu_delta / system_delta) * 100
    except Exception:
        pass
    return 0.0


def _metrics_reporter(clone_name, parent_url, interval=5):
    client = docker.from_env()
    container_id = os.getenv('HOSTNAME')
    if not container_id:
        return
    while not _metrics_stop.wait(interval):
        try:
            stats = client.containers.get(container_id).stats(stream=False)
            cpu_percent = _calculate_cpu_percent(stats)
            mem_usage = stats['memory_stats']['usage']
            mem_limit = stats['memory_stats'].get('limit', mem_usage)
            payload = {
                'clone_name': clone_name,
                'cpu_percent': cpu_percent,
                'memory_usage': mem_usage,
                'memory_limit': mem_limit,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            # Include token metrics from local token_counter
            try:
                token_data = token_counter.get_metrics()
                my_metrics = token_data['counters'].get(clone_name, {}) | token_data['costs'].get(clone_name, {})
                # Flatten into two dicts
                token_payload = {
                    'counters': token_data['counters'].get(clone_name, {}),
                    'costs': token_data['costs'].get(clone_name, {})
                }
                payload['token_metrics'] = token_payload
            except Exception:
                pass
            requests.post(parent_url.rstrip('/') + '/metrics/containers', json=payload, timeout=2)
        except Exception as e:
            print(f'[MetricsReporter error] {e}')


def _logs_forwarder(clone_name, parent_url):
    client = docker.from_env()
    container_id = os.getenv('HOSTNAME')
    if not container_id:
        return
    try:
        container = client.containers.get(container_id)
        for line in container.logs(stream=True, stdout=True, stderr=True, follow=True):
            try:
                if isinstance(line, bytes):
                    line_str = line.decode('utf-8', errors='replace').rstrip('\n')
                else:
                    line_str = line.rstrip('\n')
                payload = {
                    'clone_name': clone_name,
                    'stream': 'stdout',
                    'line': line_str,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                requests.post(parent_url.rstrip('/') + '/logs', json=[payload], timeout=2)
            except Exception:
                break
    except Exception as e:
        print(f'[LogsForwarder error] {e}')


def _trace_flusher(parent_url, interval=5):
    while not _trace_stop.wait(interval):
        with _trace_lock:
            if not _trace_spans:
                continue
            batch = list(_trace_spans)
            _trace_spans.clear()
        try:
            requests.post(parent_url.rstrip('/') + '/traces', json=batch, timeout=2)
        except Exception as e:
            print(f'[TraceFlusher error] {e}')


def _start_clone_reporters(clone_name, parent_url):
    global _metrics_thread, _logs_thread, _trace_thread
    if not _HAVE_CLONE_DEPS:
        print('[Clone reporters] docker/requests not available; skipping')
        return
    if _metrics_thread and _metrics_thread.is_alive():
        return
    _metrics_thread = threading.Thread(target=_metrics_reporter, args=(clone_name, parent_url), daemon=True)
    _metrics_thread.start()
    _logs_thread = threading.Thread(target=_logs_forwarder, args=(clone_name, parent_url), daemon=True)
    _logs_thread.start()
    _trace_thread = threading.Thread(target=_trace_flusher, args=(parent_url,), daemon=True)
    _trace_thread.start()


def record_local_span(name, start_time, end_time, attributes=None):
    trace_id = os.getenv('A0_TRACE_ID')
    if not trace_id:
        return
    span = {
        'trace_id': trace_id,
        'span_id': uuid.uuid4().hex[:16],
        'parent_span_id': None,
        'name': name,
        'start_time': start_time,
        'end_time': end_time,
        'attributes': attributes or {}
    }
    with _trace_lock:
        _trace_spans.append(span)


def _start_status_server_once():
    global _obs_server_started
    if _obs_server_started:
        return
    try:
        import threading as _th
        from status_api import run
        port = int(os.getenv('A0_OBSERVABILITY_PORT', '8080'))
        t = _th.Thread(target=lambda: run(port=port), daemon=True)
        t.start()
        _obs_server_started = True
    except Exception as e:
        print(f'[Observability] Failed to start status server: {e}')


@register_extension("agent_init")
async def on_agent_init(agent, **kwargs):
    if not agent.config.additional.get('enable_observability', False):
        return
    ctx = agent.context
    ctx.logger = StructuredLogger(agent_id=ctx.id, task_id=ctx.id)
    ctx.metrics = MetricsCollector()
    ctx.metrics.inc('agents_created')
    _start_status_server_once()
    try:
        tracing.init_tracing(service_name=f"agent-{ctx.id}")
    except Exception as e:
        ctx.logger.warning('tracing_init_failed', error=str(e))
    ctx.logger.info('agent_created', agent_name=agent.agent_name, context_id=ctx.id)
    ctx.vault = global_vault
    ctx.policy = global_policy
    try:
        audit.audit_logger.log_event(agent_id=ctx.id, event='agent_init', agent_name=agent.agent_name)
    except Exception:
        pass
    # Clone-specific reporters
    clone_name = os.getenv('A0_CLONE_NAME')
    parent_url = os.getenv('A0_PARENT_OBS_URL')
    if clone_name and parent_url and _HAVE_CLONE_DEPS:
        _start_clone_reporters(clone_name, parent_url)
        if not os.getenv('A0_TRACE_ID'):
            os.environ['A0_TRACE_ID'] = uuid.uuid4().hex


@register_extension("monologue_start")
async def on_monologue_start(agent, loop_data, **kwargs):
    if not agent.config.additional.get('enable_observability', False):
        return
    ctx = agent.context
    ctx.logger.info('monologue_start')
    ctx.metrics.inc('monologue_start')
    try:
        audit.audit_logger.log_event(agent_id=ctx.id, event='monologue_start', iteration=loop_data.iteration)
    except Exception:
        pass


@register_extension("message_loop_end")
async def on_message_loop_end(agent, loop_data, **kwargs):
    if not agent.config.additional.get('enable_observability', False):
        return
    ctx = agent.context
    ctx.logger.info('message_loop_end', iteration=loop_data.iteration)


@register_extension("monologue_end")
async def on_monologue_end(agent, loop_data, **kwargs):
    if not agent.config.additional.get('enable_observability', False):
        return
    ctx = agent.context
    ctx.logger.info('monologue_end')
    ctx.metrics.inc('tasks_completed')
    try:
        span = getattr(ctx, '_monologue_span', None)
        if span:
            span.end()
            delattr(ctx, '_monologue_span')
    except Exception:
        pass
    try:
        audit.audit_logger.log_event(agent_id=ctx.id, event='monologue_end', iteration=loop_data.iteration)
    except Exception:
        pass


@register_extension("before_main_llm_call")
async def on_before_llm(agent, loop_data, **kwargs):
    if not agent.config.additional.get('enable_observability', False):
        return
    ctx = agent.context
    _llm_start_times[id(agent)] = {'start': _time.time(), 'model': getattr(agent.config.chat_model, 'name', 'unknown')}
    try:
        tracer = tracing.get_tracer()
        if tracer:
            span_name = "llm.call"
            span = tracer.start_span(span_name)
            setattr(ctx, '_llm_span', span)
            try:
                span.set_attribute('llm.model', getattr(agent.config.chat_model, 'name', 'unknown'))
            except Exception:
                pass
    except Exception:
        pass


@register_extension("after_main_llm_call")
async def on_after_llm(agent, response, **kwargs):
    if not agent.config.additional.get('enable_observability', False):
        return
    ctx = agent.context
    start_info = _llm_start_times.pop(id(agent), None)
    end_time = _time.time()
    if start_info:
        start_time = start_info['start']
        model = start_info['model']
        duration_ms = (end_time - start_time) * 1000
        ctx.logger.info('llm_call', model=model, duration_ms=duration_ms)
        ctx.metrics.timing('llm_call_duration', duration_ms, tags={'model': model})
        ctx.metrics.inc('llm_calls')
        # Record local span for clone reporting if no OTEL tracer and we have parent_url
        tracer = tracing.get_tracer()
        parent_url = os.getenv('A0_PARENT_OBS_URL')
        if parent_url and not tracer:
            record_local_span('llm.call', start_time, end_time, attributes={
                'llm.model': model,
                'duration_ms': duration_ms,
                'status': 'success'
            })
    else:
        model = getattr(agent.config.chat_model, 'name', 'unknown')
        ctx.logger.info('llm_call', model=model)
        ctx.metrics.inc('llm_calls')

    # Token telemetry extraction and recording
    # Determine clone_id: if this is a clone, use A0_CLONE_NAME; else use 'leader' or ctx.id
    clone_id = os.getenv('A0_CLONE_NAME')
    if not clone_id:
        clone_id = 'leader'
    input_tokens = 0
    output_tokens = 0
    cost = None
    currency = 'USD'
    try:
        # Extract usage from response
        usage = None
        if isinstance(response, dict):
            usage = response.get('usage') or (response.get('choices', [{}])[0].get('usage'))
        else:
            usage = getattr(response, 'usage', None)
        if usage:
            if isinstance(usage, dict):
                input_tokens = usage.get('prompt_tokens', 0) or usage.get('input_tokens', 0)
                output_tokens = usage.get('completion_tokens', 0) or usage.get('output_tokens', 0)
            else:
                input_tokens = getattr(usage, 'prompt_tokens', 0) or getattr(usage, 'input_tokens', 0)
                output_tokens = getattr(usage, 'completion_tokens', 0) or getattr(usage, 'output_tokens', 0)
        # Compute cost using LiteLLM if available
        try:
            from litellm import completion_cost
            # If response is a litellm.ModelResponse, can call completion_cost directly
            cost = completion_cost(model=model, messages=[], completion=response)
        except Exception:
            cost = None
        # Record to token_counter
        token_counter.record(clone_id, model, input_tokens, output_tokens, cost=cost, currency=currency)
    except Exception as e:
        try:
            ctx.logger.warning('token_telemetry_error', error=str(e))
        except Exception:
            pass

    try:
        span = getattr(ctx, '_llm_span', None)
        if span:
            span.set_attribute('duration_ms', duration_ms if start_info else 0)
            span.set_attribute('status', 'success')
            span.end()
            delattr(ctx, '_llm_span')
    except Exception:
        pass
    try:
        audit.audit_logger.log_event(agent_id=ctx.id, event='llm_call', model=model, duration_ms=duration_ms if start_info else 0, status='success')
    except Exception:
        pass
