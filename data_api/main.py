from fastapi import FastAPI

from db.models import engine
from db.migrate import run_migrations
from endpoints import v1


def create_app() -> FastAPI:
    """Create a FastAPI application."""
    api = FastAPI(debug=True, title="Data API", version="1.0.0")
    api.include_router(v1.router)
    return api


app = create_app()


@app.on_event("startup")
def on_startup():
    """Run migrations on startup."""
    run_migrations()


@app.on_event("shutdown")
def on_shutdown():
    """Shutdown the database connection pool."""
    engine.dispose()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
