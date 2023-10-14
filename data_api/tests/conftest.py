from unittest import mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from db.migrate import run_migrations
from main import create_app
from util.storage import get_session


@pytest.fixture(name="engine")
def engine_fixture(postgresql):
    connection = f"postgresql+psycopg2://{postgresql.info.user}:@{postgresql.info.host}:{postgresql.info.port}/{postgresql.info.dbname}"
    engine = create_engine(url=connection, poolclass=StaticPool)
    run_migrations(engine=engine)
    return engine


@pytest.fixture(name="session")
def session_fixture(engine):
    return get_session(engine=engine)


@pytest.fixture(name="client")
def client_fixture(engine):
    with mock.patch("util.storage.default_engine", new=engine), mock.patch(
        "db.migrate.default_engine", new=engine
    ):
        app = create_app()
        with TestClient(app) as client:
            yield client
