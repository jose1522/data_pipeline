from sqlmodel import SQLModel

from db.models import engine
from util.db import wait_for_connection


def run_migrations():
    """Create database tables."""
    wait_for_connection(engine)
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    run_migrations()
