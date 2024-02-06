import time

from fastapi import Response, Request
from fastapi.logger import logger
from starlette.background import BackgroundTask
from starlette.responses import StreamingResponse
from fastapi.routing import APIRoute
from typing import Callable


def log_info(duration, status, method, path, body):
    logger.info(f"Processed request in {duration:.2f}s - {method} {path} {status} {body}")


class LoggingRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            before = time.time()
            req_body = await request.body()
            try:
                response = await original_route_handler(request)
            except Exception as e:
                duration = time.time() - before
                logger.exception(f"Failed to process request in {duration:.2f}s - {request.method} {request.url.path} {req_body} {e}")
                raise
            duration = time.time() - before

            if isinstance(response, StreamingResponse):
                res_body = b''
                async for item in response.body_iterator:
                    res_body += item

                task = BackgroundTask(log_info, duration, response.status_code, request.method, request.url.path, req_body)
                return Response(content=res_body, status_code=response.status_code,
                                headers=dict(response.headers), media_type=response.media_type, background=task)
            else:
                response.background = BackgroundTask(log_info, duration, response.status_code, request.method, request.url.path, req_body)
                return response

        return custom_route_handler