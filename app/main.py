from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.status import HTTP_422_UNPROCESSABLE_CONTENT 
from prometheus_fastapi_instrumentator import Instrumentator

from app.routers import tasks
from app.config import settings
from app.middleware.logging import LoggingMiddleware

app = FastAPI(
    title=settings.APP_NAME,
    description="Backend for LocalStorage Task Frontend - Level 1",
    version="1.0.0",
)

# metrics
instrumentator = Instrumentator(
    should_group_status_codes=True,
    should_ignore_untemplated=True,
    should_respect_env_var=True,  # gated by ENABLE_METRICS (see app.config)
    should_instrument_requests_inprogress=True,
    excluded_handlers=[f"{settings.API_V1_PREFIX}/health/", f"{settings.API_V1_PREFIX}/metrics/"],
)
instrumentator.instrument(app).expose(
    app,
    endpoint=f"{settings.API_V1_PREFIX}/metrics/",
    tags=["Monitoring"],
)

# include routers
app.include_router(tasks.router, prefix=settings.API_V1_PREFIX)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": "Validation error", "errors": errors},
    )

@app.get(f"{settings.API_V1_PREFIX}/health/")
async def health_check():
    return {"status": "ok", "level": 1, "project": "Task Manager"}