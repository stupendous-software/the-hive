import os
import sys
sys.path.insert(0, '/a0/usr/workdir')
from python.helpers.extension import register_extension
from observability import StructuredLogger, MetricsCollector
from observability import tracing

_llm_start_times = {}
_obs_server_started = False


def _start_status_server_once():
    global _obs_server_started
    if _obs_server_started:
        return
    try:
        import threading
        from status_api import run
        port = int(os.getenv('A0_OBSERVABILITY_PORT', '8080'))
        t = threading.Thread(target=lambda: run(port=port), daemon=True)
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
    # Initialize OpenTelemetry tracing if endpoint configured
    try:
        tracing.init_tracing(service_name=f"agent-{ctx.id}")
    except Exception as e:
        ctx.logger.warning('tracing_init_failed', error=str(e))
    ctx.logger.info('agent_created', agent_name=agent.agent_name, context_id=ctx.id)


@register_extension("monologue_start")
async def on_monologue_start(agent, loop_data, **kwargs):
    if not agent.config.additional.get('enable_observability', False):
        return
    ctx = agent.context
    ctx.logger.info('monologue_start')
    ctx.metrics.inc('monologue_start')
    # Create a span for the monologue if tracing enabled
    try:
        span = tracing.create_span("monologue", attributes={'phase': 'start'})
        if span:
            setattr(ctx, '_monologue_span', span)
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
    # End monologue span if exists
    try:
        span = getattr(ctx, '_monologue_span', None)
        if span:
            span.end()
            delattr(ctx, '_monologue_span')
    except Exception:
        pass


@register_extension("before_main_llm_call")
async def on_before_llm(agent, loop_data, **kwargs):
    if not agent.config.additional.get('enable_observability', False):
        return
    ctx = agent.context
    _llm_start_times[id(agent)] = _time.time()
    # Start LLM call span
    try:
        tracer = tracing.get_tracer()
        if tracer:
            span_name = "llm.call"
            span = tracer.start_span(span_name)
            setattr(ctx, '_llm_span', span)
            # Add attributes for model
            try:
                span.set_attribute('llm.model', agent.config.chat_model.name)
            except Exception:
                pass
    except Exception:
        pass


@register_extension("after_main_llm_call")
async def on_after_llm(agent, response, **kwargs):
    if not agent.config.additional.get('enable_observability', False):
        return
    ctx = agent.context
    start = _llm_start_times.pop(id(agent), None)
    if start is not None:
        duration_ms = (_time.time() - start) * 1000
        ctx.logger.info('llm_call', model=agent.config.chat_model.name, duration_ms=duration_ms)
        ctx.metrics.timing('llm_call_duration', duration_ms, tags={'model': agent.config.chat_model.name})
        ctx.metrics.inc('llm_calls')
    else:
        ctx.logger.info('llm_call', model=agent.config.chat_model.name)
        ctx.metrics.inc('llm_calls')
    # End LLM call span and add duration
    try:
        span = getattr(ctx, '_llm_span', None)
        if span:
            span.set_attribute('duration_ms', duration_ms if start else 0)
            span.set_attribute('status', 'success')
            span.end()
            delattr(ctx, '_llm_span')
    except Exception:
        pass
