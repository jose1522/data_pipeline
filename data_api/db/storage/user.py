from db.models import User
from db.models.base import BaseModel
from db.storage.base import BaseStorage
from db.storage.department import DepartmentStorage
from db.storage.job import JobStorage
from util.exceptions import BadForeignKey


class UserStorage(BaseStorage):
    def __init__(self, session):
        super().__init__(session)
        self.model = User

    def _check_fks(self, data: dict) -> None:
        job_id = data.get("job_id")
        department_id = data.get("department_id")
        if job_id:
            job_storage = JobStorage(session=self.session)
            if not job_storage.exists(job_id):
                raise BadForeignKey(fk_id=job_id, fk_name="job_id")

        if department_id:
            department_storage = DepartmentStorage(session=self.session)
            if not department_storage.exists(department_id):
                raise BadForeignKey(fk_id=department_id, fk_name="department_id")

    def update(self, id: int, data: dict) -> BaseModel:
        self._check_fks(data)
        return super().update(id, data)

    def create(self, data: BaseModel) -> BaseModel:
        user_data = {"job_id": data.job_id, "department_id": data.department_id}
        self._check_fks(user_data)
        return super().create(data)

    def upsert(self, data: dict) -> BaseModel:
        self._check_fks(data)
        return super().upsert(data)

    def bulk_upsert(self, data: list):
        jobs_seen = set()
        departments_seen = set()
        for user in data:
            job_fk = user.get("job_id")
            department_fk = user.get("department_id")
            user_fks = {}
            if job_fk not in jobs_seen:
                user_fks["job_id"] = job_fk
                jobs_seen.add(job_fk)
            if department_fk not in departments_seen:
                user_fks["department_id"] = department_fk
                departments_seen.add(department_fk)
            self._check_fks(user_fks)
        return super().bulk_upsert(data)
