import time

from sqlalchemy.exc import OperationalError


def wait_for_connection(engine):
    print("Connecting to the database")
    for _ in range(30):  # Retry for 30 times
        try:
            # Attempt to create a new connection
            connection = engine.connect()
        except OperationalError:
            print("Database not available, waiting...")
            time.sleep(1)  # Wait for 1 second before retrying
        else:
            # If the connection is successful, close it and break out of the loop
            print("Connected to the database")
            connection.close()
            break
    else:
        # If the database is not reachable after 30 retries, raise an exception
        raise Exception("Could not connect to the database")