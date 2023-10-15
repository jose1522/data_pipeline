from datetime import datetime
from typing import Optional

from pydantic import BaseModel as PydanticBase, constr

from db.schemas.department import DepartmentResponse
from db.schemas.job import JobResponse


class UserInsert(PydanticBase):
    """Base model for a user. This is the model that is used for validation."""

    id: Optional[int]
    name: constr(min_length=1, max_length=255)
    datetime: datetime
    job_id: int
    department_id: int

    def dict(self, *args, **kwargs):
        output = super().dict(*args, **kwargs)
        if not output["id"]:
            del output["id"]
        return output


class UserResponse(PydanticBase):
    id: int
    name: str
    datetime: datetime
    job: Optional[JobResponse]
    department: Optional[DepartmentResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
