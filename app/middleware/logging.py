import json
import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings

# Use a dedicated logger — uvicorn.access expects a 5-tuple access record,
# not an arbitrary message/dict.
logger = logging.getLogger("app.access")
logger.setLevel(logging.INFO)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        process_time = (time.time() - start_time) * 1000  # milliseconds

        log_data = {
            "timestamp": time.time(),
            "level": "INFO",
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(process_time, 2),
            "client_host": request.client.host if request.client else "unknown",
            "env": settings.APP_ENV,
            "service": "fastapi-task-api",
        }

        logger.info(json.dumps(log_data))

        return response
