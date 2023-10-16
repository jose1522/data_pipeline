import io
from datetime import datetime
from typing import Optional

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from reports.user import quarterly_hires, department_hires
from util.streaming import buffer_to_generator

router = APIRouter(prefix="/report", tags=["report"])


@router.get("/quarterly_hires", description="Download quarterly hires")
def get_quarterly_hires(year: Optional[int] = None):
    year = year or datetime.now().year
    data = quarterly_hires(year)
    headers = {
        "Content-Disposition": f"attachment; filename=quarterly_hires_{year}.csv"
    }
    buffer = io.StringIO()
    data.to_csv(buffer, index=False)

    return StreamingResponse(
        buffer_to_generator(buffer), media_type="text/csv", headers=headers
    )


@router.get("/department_hires", description="Download department hires")
def get_department_hires(year: Optional[int] = None):
    year = year or datetime.now().year
    data = department_hires(year)
    headers = {
        "Content-Disposition": f"attachment; filename=department_hires_{year}.csv"
    }
    buffer = io.StringIO()
    data.to_csv(buffer, index=False)
    return StreamingResponse(
        buffer_to_generator(buffer), media_type="text/csv", headers=headers
    )
