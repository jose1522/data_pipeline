from typing import List

from fastapi import APIRouter, Header
from sqlalchemy.exc import IntegrityError

from db.schemas.job import JobInsert, JobsListInsert, JobResponse
from db.storage.job import JobStorage
from util.exceptions import RecordAlreadyExists
from util.storage import get_session

router = APIRouter(prefix="/job", tags=["job"])


@router.post("/", response_model=JobResponse, status_code=201)
async def create_job(job: JobInsert):
    session = get_session()
    storage = JobStorage(session=session)
    job = storage.upsert(job.dict())
    session.commit()
    session.refresh(job)
    return job


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: int):
    session = get_session()
    storage = JobStorage(session=session)
    db_obj = storage.read(job_id)
    return db_obj


@router.get("/", response_model=List[JobResponse])
async def get_jobs(limit: int = 10, offset: int = 0):
    session = get_session()
    storage = JobStorage(session=session)
    db_obj = storage.all(limit=limit, skip=offset)
    return db_obj


@router.patch("/{job_id}", response_model=JobResponse)
async def update_job(job_id: int, job: JobInsert):
    session = get_session()
    storage = JobStorage(session=session)
    db_obj = storage.update(job_id, job.dict())
    try:
        session.commit()
    except IntegrityError:
        raise RecordAlreadyExists(data=job.dict())
    session.refresh(db_obj)
    return db_obj


@router.delete("/{job_id}", status_code=204)
async def delete_job(
    job_id: int,
    x_soft_delete: bool = Header(default=True),
):
    session = get_session()
    storage = JobStorage(session=session)
    storage.delete(job_id, soft_delete=x_soft_delete)
    session.commit()


@router.post("/bulk", status_code=201)
async def bulk_insert(jobs: JobsListInsert):
    session = get_session()
    storage = JobStorage(session=session)
    storage.bulk_upsert([job.dict() for job in jobs.jobs])
    session.commit()
