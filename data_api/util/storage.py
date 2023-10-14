from sqlalchemy.orm import sessionmaker, Session as BaseSession

from db.models import engine as default_engine


class Session(BaseSession):
    def commit(self) -> None:
        try:
            super().commit()
        except Exception as e:
            self.rollback()
            raise e


def get_session(engine: default_engine = None):
    """Get a session from the sessionmaker.
    Args:
        engine (Engine): The engine to use for the session. Defaults to None.
    Returns:
        Session: A session object.
    """
    engine = engine or default_engine
    session = sessionmaker(bind=engine, autocommit=False, class_=Session)
    session = session()
    return session
