from db.models import Department
from db.storage.base import BaseStorage


class DepartmentStorage(BaseStorage):
    def __init__(self, session):
        super().__init__(session)
        self.model = Department
