from db.models import Job
from db.storage.base import BaseStorage


class JobStorage(BaseStorage):
    def __init__(self, session):
        super().__init__(session)
        self.model = Job
