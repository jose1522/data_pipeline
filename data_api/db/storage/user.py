from db.models import User
from db.storage.base import BaseStorage


class UserStorage(BaseStorage):
    def __init__(self, session):
        super().__init__(session)
        self.model = User
