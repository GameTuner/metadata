# Copyright (c) 2024 AlgebraAI All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
from metadata.core.domain.common import EntityError, EntityNotFound
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry import trace
from fastapi import FastAPI
from fastapi.logger import logger
from fastapi.responses import PlainTextResponse
from metadata.config import settings
from metadata.core.database import orm, connection
from metadata import status_maintainer
from metadata import monitoring
from metadata.logging.setup_logging import setup_logging
from metadata.logging.middleware import LoggingMiddleware
from metadata.api.app.web import router as app_router
from metadata.api.healthcheck.web import router as healthcheck_router
from metadata.api.event.web import router as event_router


app = FastAPI()

if settings.JSON_LOGS == '1':
    tracer_provider = TracerProvider()
    cloud_trace_exporter = CloudTraceSpanExporter()
    tracer_provider.add_span_processor(BatchSpanProcessor(cloud_trace_exporter))
    trace.set_tracer_provider(tracer_provider)

    setup_logging()
    app.add_middleware(LoggingMiddleware)
else:
    logger.handlers = []
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"))
    logger.addHandler(console_handler)
    logger.setLevel(logging.DEBUG)

app.include_router(app_router)
app.include_router(event_router)
app.include_router(healthcheck_router)


@app.exception_handler(EntityError)
async def entity_error_exception_handler(request, exc):
    return PlainTextResponse(str(exc), status_code=400)


@app.exception_handler(EntityNotFound)
async def entity_not_found_exception_handler(request, exc):
    return PlainTextResponse(str(exc), status_code=404)

orm.init_orm_mappers()


if settings.RUN_MAINTAINER == '1':
    monitoring.start()
    status_maintainer.start(connection.get_db_session, settings.SCHEMA_BUCKET_NAME, settings.BIGQUERY_REGION, False)
else:
    status_maintainer.start(connection.get_db_session, '', '', True)
