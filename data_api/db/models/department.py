from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from db.models.base import BaseModel


class Department(BaseModel):
    __tablename__ = "department"
    department = Column(String(255), nullable=False, unique=True, index=True)
    users = relationship("User", back_populates="department")
