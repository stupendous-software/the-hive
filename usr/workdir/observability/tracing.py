import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

_tracer = None


def init_tracing(service_name: str = "agent-zero"):
    global _tracer
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not endpoint:
        _tracer = None
        return
    resource = Resource(attributes={
        "service.name": os.getenv("OTEL_SERVICE_NAME", service_name)
    })
    provider = TracerProvider(resource=resource)
    try:
        exporter = OTLPSpanExporter(endpoint=endpoint)
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)
        _tracer = trace.get_tracer(__name__)
    except Exception as e:
        print(f"[Tracing] init failed: {e}")
        _tracer = None


def get_tracer():
    return _tracer


def create_span(name, parent=None, attributes=None):
    if _tracer is None:
        class Dummy:
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def set_attribute(self, *a, **k): pass
            def add_event(self, *a, **k): pass
        return Dummy()
    ctx = trace.set_span_in_context(parent) if parent else None
    return _tracer.start_as_current_span(name, context=ctx, attributes=attributes or {})
