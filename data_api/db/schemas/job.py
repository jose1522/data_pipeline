from datetime import datetime
from typing import Optional

from pydantic import BaseModel as PydanticBase


class JobInsert(PydanticBase):
    """Base model for a department. This is the model that is used for validation."""

    id: Optional[int]
    job: str

    def dict(self, *args, **kwargs):
        output = super().dict(*args, **kwargs)
        if not output["id"]:
            del output["id"]
        return output


class JobResponse(PydanticBase):
    """Represents a list of departments to insert."""

    id: int
    job: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
