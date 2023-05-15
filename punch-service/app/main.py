from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from app.api.router import router
from app.core.config import settings


def get_application():
    _app = FastAPI(title=settings.PROJECT_NAME)

    @_app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            dict(detail=exc.errors()),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    _app.include_router(router, prefix="/api")

    return _app

app = get_application()
