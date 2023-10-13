from sqlmodel import Field, SQLModel

from db.models.base import BaseModel


class DepartmentBase(SQLModel):
    """Base model for a department. This is the model that is used for validation."""

    department: str = Field(nullable=False, unique=True, min_length=1, max_length=255)


class Department(DepartmentBase, BaseModel, table=True):
    """Represents a department in the company."""


class DepartmentListInsert(SQLModel):
    """Represents a list of departments to insert."""
    departments: list[DepartmentBase]