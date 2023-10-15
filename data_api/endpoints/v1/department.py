from typing import List

from fastapi import APIRouter, Header
from pydantic import conlist
from sqlalchemy.exc import IntegrityError

from db.schemas.department import (
    DepartmentInsert,
    DepartmentResponse,
)
from db.storage.department import DepartmentStorage
from util.exceptions import RecordAlreadyExists
from util.storage import get_session

router = APIRouter(prefix="/department", tags=["department"])


@router.post("/", response_model=DepartmentResponse, status_code=201)
async def create_job(department: DepartmentInsert):
    session = get_session()
    storage = DepartmentStorage(session=session)
    department = storage.upsert(department.dict())
    session.commit()
    session.refresh(department)
    return department


@router.get("/{department_id}", response_model=DepartmentResponse)
async def get_job(department_id: int):
    session = get_session()
    storage = DepartmentStorage(session=session)
    db_obj = storage.read(department_id)
    return db_obj


@router.get("/", response_model=List[DepartmentResponse])
async def get_jobs(limit: int = 10, offset: int = 0):
    session = get_session()
    storage = DepartmentStorage(session=session)
    db_obj = storage.all(limit=limit, skip=offset)
    return db_obj


@router.patch("/{department_id}", response_model=DepartmentResponse)
async def update_job(department_id: int, job: DepartmentInsert):
    session = get_session()
    storage = DepartmentStorage(session=session)
    db_obj = storage.update(department_id, job.dict())
    try:
        session.commit()
    except IntegrityError:
        raise RecordAlreadyExists(data=job.dict())
    session.refresh(db_obj)
    return db_obj


@router.delete("/{department_id}", status_code=204)
async def delete_job(
    department_id: int,
    x_soft_delete: bool = Header(default=True),
):
    session = get_session()
    storage = DepartmentStorage(session=session)
    storage.delete(department_id, soft_delete=x_soft_delete)
    session.commit()


@router.post("/bulk", status_code=201)
async def bulk_insert(
    departments: conlist(DepartmentInsert, min_items=1, max_items=1000)
):
    session = get_session()
    storage = DepartmentStorage(session=session)
    storage.bulk_upsert([department.dict() for department in departments])
    session.commit()
