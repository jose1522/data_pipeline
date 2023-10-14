from datetime import datetime

from pydantic import BaseModel as PydanticBase, constr


class DepartmentInsert(PydanticBase):
    """Base model for a department. This is the model that is used for validation."""

    department: constr(min_length=1, max_length=255)


class DepartmentResponse(PydanticBase):
    id: int
    department: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
