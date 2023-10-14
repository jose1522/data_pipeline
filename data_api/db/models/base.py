from datetime import datetime

from sqlalchemy import Column, DateTime, Boolean, BigInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True
    )
    deleted_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, index=True, nullable=True)

    def soft_delete(self):
        self.is_active = False
        self.deleted_at = datetime.utcnow()

    def update(self, data: dict):
        for key, value in data.items():
            setattr(self, key, value)
