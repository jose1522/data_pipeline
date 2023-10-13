from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel

from db.models.base import BaseModel
from db.models.department import Department
from db.models.job import Job


class BaseUser(SQLModel):
    """Base model for a user. This is the model that is used for validation."""

    name: str = Field(nullable=False, min_length=1, max_length=255)
    datetime: Optional[str] = Field(
        nullable=True, max_length=255, regex=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$"
    )
    job_id: Optional[int] = Field(default=None, foreign_key=Job.id)
    department_id: Optional[int] = Field(default=None, foreign_key=Department.id)


class User(BaseUser, BaseModel, table=True):
    # Add a unique constraint to the table to prevent duplicate entries.
    # The combination of name, job_id, and department_id must be unique.
    __table_args__ = (UniqueConstraint("name", "job_id", "department_id"),)
