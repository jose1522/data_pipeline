from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session as _Session

from db.models import engine


class Session(_Session):
    def commit(self):
        """Override the commit method to rollback on error."""
        try:
            super().commit()
        except SQLAlchemyError as e:
            self.rollback()
            raise e


def get_session():
    with Session(engine) as session:
        yield session
