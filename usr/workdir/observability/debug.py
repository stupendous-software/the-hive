from functools import wraps
import time as _time
from observability import tracing
import audit  # global audit_logger
from policy import policy_engine, PolicyViolation

def log_tool_call(logger):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            tracer = tracing.get_tracer()
            span = None
            if tracer:
                span_name = f"tool.{func.__name__}"
                span = tracer.start_span(span_name)
                try:
                    from opentelemetry import trace
                    token = trace.set_span_in_context(span)
                except Exception:
                    token = None
            # Policy enforcement
            agent_id = getattr(logger, 'agent_id', 'unknown')
            try:
                if not policy_engine.check(agent_id, func.__name__):
                    # Audit and raise
                    try:
                        audit.audit_logger.log_event(agent_id=agent_id, event='policy_violation', tool=func.__name__, reason='denied by policy')
                    except Exception:
                        pass
                    raise PolicyViolation(f"Tool {func.__name__} denied by policy for agent {agent_id}")
            except Exception as e:
                # Unexpected policy engine error – deny and raise
                raise

            start = _time.time()
            try:
                result = await func(*args, **kwargs)
                duration_ms = (_time.time() - start) * 1000
                logger.info('tool_call', tool=func.__name__, duration_ms=duration_ms, status='success')
                if span:
                    span.set_attribute('tool.name', func.__name__)
                    span.set_attribute('duration_ms', duration_ms)
                    span.set_attribute('status', 'success')
                try:
                    audit.audit_logger.log_event(agent_id=agent_id, event='tool_call', tool=func.__name__, duration_ms=duration_ms, status='success')
                except Exception:
                    pass
                return result
            except Exception as e:
                duration_ms = (_time.time() - start) * 1000
                logger.info('tool_call', tool=func.__name__, duration_ms=duration_ms, status='error', error=str(e))
                if span:
                    span.set_attribute('tool.name', func.__name__)
                    span.set_attribute('duration_ms', duration_ms)
                    span.set_attribute('status', 'error')
                    span.record_exception(e)
                try:
                    audit.audit_logger.log_event(agent_id=agent_id, event='tool_call', tool=func.__name__, duration_ms=duration_ms, status='error', error=str(e))
                except Exception:
                    pass
                raise
            finally:
                if span:
                    try:
                        span.end()
                    except Exception:
                        pass
                    try:
                        if 'token' in locals():
                            trace.detach(token)
                    except Exception:
                        pass
        return wrapper
    return decorator
