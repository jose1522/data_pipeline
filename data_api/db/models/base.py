from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger
from sqlmodel import SQLModel, Field


class BaseModel(SQLModel):
    id: Optional[int] = Field(
        primary_key=True, index=True, default=None, sa_column=BigInteger
    )
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(default=None, nullable=True, exclude=True)
    is_active: Optional[bool] = Field(default=True, index=True, exclude=True)

    def soft_delete(self):
        self.is_active = False
        self.deleted_at = datetime.utcnow()

    def update(self, data: dict):
        for key, value in data.items():
            setattr(self, key, value)
        self.updated_at = datetime.utcnow()


class BaseDelete(BaseModel):
    id: int
