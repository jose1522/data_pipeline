import time

import pandas as pd
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError

from util.logger import get_logger


def wait_for_connection(engine):
    logger = get_logger()
    logger.info("Connecting to the database")
    for _ in range(30):  # Retry for 30 times
        try:
            # Attempt to create a new connection
            connection = engine.connect()
        except OperationalError:
            logger.info("Database not available, waiting...")
            time.sleep(1)  # Wait for 1 second before retrying
        else:
            # If the connection is successful, close it and break out of the loop
            logger.info("Connected to the database")
            connection.close()
            break
    else:
        # If the database is not reachable after 30 retries, raise an exception
        raise Exception("Could not connect to the database")


def query_to_dataframe(query: str, engine: Engine) -> pd.DataFrame:
    """Executes a SQL query and returns a dataframe.
    Args:
        query: The SQL query to execute.
        engine: The SQLAlchemy engine to use.
    """
    return pd.read_sql_query(query, engine)
