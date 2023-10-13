from sqlmodel import create_engine
from .department import Department
from .job import Job
from .user import User
import config

engine = create_engine(url=config.DB_DSN, echo=config.DB_ECHO)

__all__ = [engine, Department, Job, User]
