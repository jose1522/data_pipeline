from pydantic import conlist
from sqlmodel import Field, SQLModel

from db.models.base import BaseModel


class JobBase(SQLModel):
    """Base model for a department. This is the model that is used for validation."""

    job: str = Field(nullable=False, unique=True, min_length=1, max_length=255)


class Job(JobBase, BaseModel, table=True):
    """Represents a department in the company."""


class JobsListInsert(BaseModel):
    jobs: conlist(JobBase, min_items=1, max_items=1000)
