from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    UniqueConstraint,
    DateTime,
)
from sqlalchemy.orm import relationship

from db.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "user"
    name = Column(String(255), nullable=False, index=True)
    datetime = Column(DateTime)
    job_id = Column(Integer, ForeignKey("job.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("department.id"), nullable=False)
    job = relationship(
        "Job",
        back_populates="users",
        primaryjoin="and_(Job.id==User.job_id, Job.is_active==True)",
    )
    department = relationship(
        "Department",
        back_populates="users",
        primaryjoin="and_(Department.id==User.department_id, Department.is_active==True)",
    )

    __table_args__ = (UniqueConstraint("name", "job_id", "department_id"),)
