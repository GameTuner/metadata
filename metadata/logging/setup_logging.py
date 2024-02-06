import logging

import google.cloud.logging
from fastapi.logger import logger
from google.cloud.logging_v2.handlers import CloudLoggingHandler

from metadata.logging.filter import GoogleCloudLogFilter


def setup_logging():
    client = google.cloud.logging.Client()
    handler = CloudLoggingHandler(client, name="gametuner-metadata")
    handler.setLevel(logging.DEBUG)
    handler.filters = []
    handler.addFilter(GoogleCloudLogFilter(project=client.project))
    logger.handlers = []
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

