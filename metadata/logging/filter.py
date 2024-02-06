import logging

from google.cloud.logging_v2.handlers import CloudLoggingFilter

from metadata.logging.middleware import http_request_context, cloud_trace_context


class GoogleCloudLogFilter(CloudLoggingFilter):

    def filter(self, record: logging.LogRecord) -> bool:
        if http_request_context.get():
            record.http_request = http_request_context.get()

            trace = cloud_trace_context.get()
            if trace:
                record.trace = f"projects/{self.project}/traces/{trace['trace']}"
                record.span_id = trace["span_id"]
        super().filter(record)
        return True
