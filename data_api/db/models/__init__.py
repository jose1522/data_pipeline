from sqlalchemy import create_engine

import config
from .department import Department
from .job import Job
from .user import User

engine = create_engine(url=config.DB_DSN, echo=config.DB_ECHO)

__all__ = [engine, Department, Job, User]
