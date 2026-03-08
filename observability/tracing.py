import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

_tracer = None


def init_tracing(service_name: str = "agent-zero"):
    """Initialize OpenTelemetry tracing if OTEL_EXPORTER_OTLP_ENDPOINT is set.
    
    Environment variables:
    - OTEL_EXPORTER_OTLP_ENDPOINT: URL to send traces (e.g., http://localhost:4318/v1/traces)
    - OTEL_SERVICE_NAME: override service name (default: agent-zero)
    """
    global _tracer
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not endpoint:
        # Tracing disabled
        _tracer = None
        return
    
    resource = Resource(attributes={
        "service.name": os.getenv("OTEL_SERVICE_NAME", service_name)
    })
    provider = TracerProvider(resource=resource)
    
    try:
        exporter = OTLPSpanExporter(endpoint=endpoint)
        processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
        _tracer = trace.get_tracer(__name__)
    except Exception as e:
        print(f"[Tracing] Failed to initialize: {e}")
        _tracer = None


def get_tracer():
    """Return the initialized tracer or None if tracing is disabled."""
    return _tracer


def create_span(name, parent=None, attributes=None):
    """Create a new span as a context manager if tracing is enabled.
    
    Usage:
        with create_span("my_operation") as span:
            # do work
            span.set_attribute("key", "value")
    """
    if _tracer is None:
        # Return a dummy context manager that does nothing
        class DummySpan:
            def __enter__(self): return self
            def __exit__(self, exc_type, exc_val, exc_tb): return False
            def set_attribute(self, key, value): pass
            def add_event(self, name, attributes=None): pass
        return DummySpan()
    
    if parent is not None:
        context = trace.set_span_in_context(parent)
        return _tracer.start_as_current_span(name, context=context, attributes=attributes or {})
    else:
        return _tracer.start_as_current_span(name, attributes=attributes or {})
