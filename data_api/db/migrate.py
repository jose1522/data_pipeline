from sqlmodel import SQLModel

from db.models import engine


def run_migrations():
    """Create database tables."""
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    run_migrations()
