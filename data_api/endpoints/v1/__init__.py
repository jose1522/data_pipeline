from fastapi import APIRouter
from endpoints.v1.department import router as department_router
from endpoints.v1.job import router as job_router
from endpoints.v1.user import router as user_router
from endpoints.v1.report import router as report_router

router = APIRouter(prefix="/v1")
router.include_router(department_router)
router.include_router(job_router)
router.include_router(user_router)
router.include_router(report_router)

__all__ = ["router"]
