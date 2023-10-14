from typing import List

from fastapi import APIRouter, Depends, Header

from db.models import Department
from db.models.department import DepartmentBase, DepartmentListInsert
from db.storage.department import DepartmentStorage
from util.storage import get_session

router = APIRouter(prefix="/department", tags=["department"])


@router.post("/", response_model=Department, status_code=201)
async def create_job(department: DepartmentBase, session=Depends(get_session)):
    storage = DepartmentStorage(session=session)
    department = storage.upsert(department.dict())
    session.commit()
    session.refresh(department)
    return department


@router.get("/{department_id}", response_model=Department)
async def get_job(department_id: int, session=Depends(get_session)):
    storage = DepartmentStorage(session=session)
    db_obj = storage.read(department_id)
    return db_obj


@router.get("/", response_model=List[Department])
async def get_jobs(session=Depends(get_session), limit: int = 10, offset: int = 0):
    storage = DepartmentStorage(session=session)
    db_obj = storage.all(limit=limit, skip=offset)
    return db_obj


@router.patch("/{department_id}", response_model=Department)
async def update_job(
    department_id: int, job: DepartmentBase, session=Depends(get_session)
):
    storage = DepartmentStorage(session=session)
    db_obj = storage.update(department_id, job.dict())
    session.commit()
    session.refresh(db_obj)
    return db_obj


@router.delete("/{department_id}", status_code=204)
async def delete_job(
    department_id: int,
    x_soft_delete: bool = Header(default=True),
    session=Depends(get_session),
):
    storage = DepartmentStorage(session=session)
    storage.delete(department_id, soft_delete=x_soft_delete)
    session.commit()


@router.post("/bulk", status_code=201)
async def bulk_insert(departments: DepartmentListInsert, session=Depends(get_session)):
    storage = DepartmentStorage(session=session)
    storage.bulk_upsert([department.dict() for department in departments.departments])
    session.commit()
