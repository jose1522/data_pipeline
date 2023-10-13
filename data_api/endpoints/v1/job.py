from fastapi import APIRouter, Depends, HTTPException

from db.models import Job
from db.models.job import JobBase
from db.storage.job import JobStorage
from util.storage import get_session

router = APIRouter(prefix="/job", tags=["job"])


@router.post("/", response_model=Job, status_code=201)
async def create_job(job: JobBase, session=Depends(get_session)):
    storage = JobStorage(session=session)
    job = storage.upsert(job.dict())
    session.commit()
    session.refresh(job)
    return job


@router.get("/{job_id}", response_model=Job)
async def get_job(job_id: int, session=Depends(get_session)):
    storage = JobStorage(session=session)
    db_obj = storage.read(job_id, is_active_only=False)
    if db_obj:
        if db_obj.is_active:
            return db_obj
        raise HTTPException(status_code=204)
    raise HTTPException(status_code=404, detail="Job not found")


@router.patch("/{job_id}", response_model=Job)
async def update_job(job_id: int, job: JobBase, session=Depends(get_session)):
    storage = JobStorage(session=session)
    if not storage.exists(job_id):
        raise HTTPException(status_code=404, detail="Job not found")
    db_obj = storage.update(job_id, job.dict())
    session.commit()
    session.refresh(db_obj)
    return db_obj


@router.delete("/{job_id}", status_code=204)
async def delete_job(job_id: int, soft_delete: bool = True, session=Depends(get_session)):
    storage = JobStorage(session=session)
    storage.delete(job_id, soft_delete=soft_delete)
    session.commit()
