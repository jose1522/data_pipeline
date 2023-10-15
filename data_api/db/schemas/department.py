from datetime import datetime
from typing import Optional

from pydantic import BaseModel as PydanticBase, constr


class DepartmentInsert(PydanticBase):
    """Base model for a department. This is the model that is used for validation."""

    id: Optional[int]
    department: constr(min_length=1, max_length=255)

    def dict(self, *args, **kwargs):
        output = super().dict(*args, **kwargs)
        if not output["id"]:
            del output["id"]
        return output


class DepartmentResponse(PydanticBase):
    id: int
    department: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
