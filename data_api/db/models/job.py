from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from db.models.base import BaseModel


class Job(BaseModel):
    __tablename__ = "job"
    job = Column(String(255), nullable=False, unique=True, index=True)
    users = relationship("User", back_populates="job", cascade="all, delete")
