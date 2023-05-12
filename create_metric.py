import imp
from google.cloud import monitoring_v3
from google.cloud.monitoring_v3 import Point, TimeInterval,SpanContext
from google.api.distribution_pb2 import Distribution
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.any_pb2 import Any
import random
import time
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter
)

SERVICE_NAME="opentelemetry-testing"
provider = TracerProvider(
    resource=Resource.create({SERVICE_NAME:SERVICE_NAME})
)

processor = BatchSpanProcessor(
    ConsoleSpanExporter(),
)
provider.add_span_processor(processor)
# Sets the global default tracer provider
trace.set_tracer_provider(provider)
# Creates a tracer from the global tracer provider
tracer = trace.get_tracer(__name__)



def _timestamp_from_nanos(nanos: int) -> Timestamp:
    ts = Timestamp()
    ts.FromNanoseconds(nanos)
    return ts




now = time.time()
seconds = int(now)
nanos = int(
    (now-seconds) * 10 ** 9 
)
interval = TimeInterval(
    {
        "end_time": {
            "seconds": seconds,
            "nanos": nanos
        }
    }
)

def generate_attachments_withspancontext(span_ctx: SpanContext):
    return span_ctx

def generate_attachment_any(span_ctx: SpanContext):
    any = Any()
    any.type_url = "type.googleapis.com/google.monitoring.v3.SpanContext"
    span_name = span_ctx.span_name
    any.value = str.encode(span_name)
    return any


with tracer.start_as_current_span("demo") as span:
    project=""
    trace_id = trace.format_trace_id(span.get_span_context().trace_id)
    span_id = trace.format_span_id(span.get_span_context().span_id)
    span_ctx = SpanContext(
        span_name=f"projects/{project}/traces/{trace_id}/spans{span_id}"
    )
    point = Point(
        {
            "interval": interval,
            "value": {
                "distribution_value": {
                    "count": 5,
                    "mean": 20,
                    "bucket_counts": [0, 0, 4, 0, 1],
                    "bucket_options":{
                        "explicit_buckets": {
                            "bounds": [5.0, 10.0, 25.0, 50.0, 100.0]
                        }
                    },
                    "exemplars":[
                        {
                            "timestamp": _timestamp_from_nanos(time.time_ns()),
                            "attachments": [
                                generate_attachments_withspancontext(span_ctx)
                                # generate_attachment_any(span_ctx)
                            ],
                            "value": random.uniform(10,25)
                        }
                    ]
                }
            }
        }
    )

    print(point)

"""
====================================================================================================
generate_attachments_withspancontext reuslt get error 
====================================================================================================

Traceback (most recent call last):
  File "/Users/abehsu/Library/Caches/pypoetry/virtualenvs/gcp-monitoring-lGmAGX-S-py3.10/lib/python3.10/site-packages/proto/marshal/rules/message.py", line 36, in to_proto
    return self._descriptor(**value)
TypeError: Parameter to MergeFrom() must be instance of same class: expected <class 'google.protobuf.any_pb2.Any'> got <class 'google.cloud.monitoring_v3.types.span_context.SpanContext'>.

====================================================================================================
generate_attachment_any reuslt (I don't knwo this is correct or not)
====================================================================================================


interval {
  end_time {
    seconds: 1683917849
    nanos: 114447116
  }
}
value {
  distribution_value {
    count: 5
    mean: 20
    bucket_options {
      explicit_buckets {
        bounds: 5
        bounds: 10
        bounds: 25
        bounds: 50
        bounds: 100
      }
    }
    bucket_counts: 0
    bucket_counts: 0
    bucket_counts: 4
    bucket_counts: 0
    bucket_counts: 1
    exemplars {
      value: 15.333750185282106
      timestamp {
        seconds: 1683917849
        nanos: 117479000
      }
      attachments {
        type_url: "type.googleapis.com/google.monitoring.v3.SpanContext"
        value: "projects//traces/7c214d18ac67588bc8250e42bb7f8a81/spansa8d3f1261395ecd8"
      }
    }
  }
}
"""