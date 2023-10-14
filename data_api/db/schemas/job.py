from datetime import datetime

from pydantic import BaseModel as PydanticBase, conlist


class JobInsert(PydanticBase):
    """Base model for a department. This is the model that is used for validation."""

    job: str


class JobResponse(PydanticBase):
    """Represents a list of departments to insert."""

    id: int
    job: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class JobsListInsert(PydanticBase):
    jobs: conlist(JobInsert, min_items=1, max_items=1000)
