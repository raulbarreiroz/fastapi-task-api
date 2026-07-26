from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.status import HTTP_422_UNPROCESSABLE_CONTENT 

from app.routers import tasks
from app.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="Backend for LocalStorage Task Frontend - Level 1",
    version="1.0.0",
)

app.include_router(tasks.router, prefix=settings.API_V1_PREFIX)

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