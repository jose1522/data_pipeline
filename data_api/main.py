from fastapi import FastAPI

from db.migrate import run_migrations
from db.models import engine
from endpoints import v1
from util.exceptions import override_default_handlers
from util.logger import get_logger
from util.middleware import ExceptionMiddleware, LoggingMiddleware


def create_app() -> FastAPI:
    """Create a FastAPI application."""
    api = FastAPI(debug=True, title="Data API", version="1.0.0")
    api.add_middleware(ExceptionMiddleware)
    api.add_middleware(LoggingMiddleware)
    api.include_router(v1.router)
    override_default_handlers(api)
    return api


app = create_app()


@app.on_event("startup")
def on_startup():
    """Run migrations on startup."""
    logger = get_logger()
    logger.info("Running migrations...")
    run_migrations()
    logger.info("Migrations complete.")


@app.on_event("shutdown")
def on_shutdown():
    """Shutdown the database connection pool."""
    engine.dispose()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
