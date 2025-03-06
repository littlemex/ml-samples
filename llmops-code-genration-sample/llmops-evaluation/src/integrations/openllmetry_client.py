from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
import os
from dotenv import load_dotenv

load_dotenv()

class OpenLLMetryClient:
    def __init__(self):
        resource = Resource.create({"service.name": os.getenv("OTEL_SERVICE_NAME", "llm-evaluation")})
        
        # トレース設定
        trace_provider = TracerProvider(resource=resource)
        otlp_span_exporter = OTLPSpanExporter(endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"))
        trace_provider.add_span_processor(BatchSpanProcessor(otlp_span_exporter))
        trace.set_tracer_provider(trace_provider)
        self.tracer = trace.get_tracer(__name__)

        # メトリクス設定
        metric_reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"))
        )
        metric_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
        metrics.set_meter_provider(metric_provider)
        self.meter = metrics.get_meter(__name__)

        # カウンターとヒストグラムの初期化
        self.request_counter = self.meter.create_counter(
            name="llm_requests",
            description="Number of LLM requests"
        )
        self.latency_histogram = self.meter.create_histogram(
            name="llm_latency",
            description="Latency of LLM requests",
            unit="ms"
        )
        self.token_counter = self.meter.create_counter(
            name="llm_tokens",
            description="Number of tokens used"
        )

    def record_request(self, model: str, success: bool = True):
        self.request_counter.add(1, {"model": model, "success": str(success)})

    def record_latency(self, model: str, latency_ms: float):
        self.latency_histogram.record(latency_ms, {"model": model})

    def record_tokens(self, model: str, token_count: int, token_type: str):
        self.token_counter.add(token_count, {
            "model": model,
            "type": token_type  # "prompt" or "completion"
        })

    def create_span(self, name: str):
        return self.tracer.start_span(name)