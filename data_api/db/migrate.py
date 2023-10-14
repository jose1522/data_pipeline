from db.models import engine as default_engine
from db.models.base import Base
from util.db import wait_for_connection


def run_migrations(engine: default_engine = None):
    """Create database tables."""
    engine = engine or default_engine
    wait_for_connection(engine)
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    run_migrations()
