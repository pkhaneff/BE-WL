from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.api.exception_handlers import (
    domain_error_handler,
    application_error_handler,
    infrastructure_error_handler,
    invalid_token_handler,
)
from app.core.config import settings
from app.core.exceptions import (
    DomainError,
    ApplicationError,
    InfrastructureError,
    InvalidTokenError,
)
from app.core.logging import setup_logging, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    setup_logging(debug=settings.APP_DEBUG)
    logger.info(
        "app_startup",
        app_name=settings.APP_NAME,
        env=settings.APP_ENV,
    )
    yield
    logger.info("app_shutdown")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        description="Backend API cho ứng dụng Wishlist - môi trường dành cho các cặp đôi.",
        docs_url="/docs" if settings.APP_DEBUG else None,
        redoc_url="/redoc" if settings.APP_DEBUG else None,
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.APP_DEBUG else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    app.add_exception_handler(DomainError, domain_error_handler)
    app.add_exception_handler(ApplicationError, application_error_handler)
    app.add_exception_handler(InfrastructureError, infrastructure_error_handler)
    app.add_exception_handler(InvalidTokenError, invalid_token_handler)

    # Routers
    app.include_router(api_router)

    @app.get("/health", tags=["Health"])
    def health_check() -> dict:
        return {"status": "ok", "app": settings.APP_NAME, "env": settings.APP_ENV}

    return app


app = create_app()
