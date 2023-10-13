class RecordNotFound(Exception):
    def __init__(self, record_id: str):
        self.record_id = record_id
        self.message = f"Record with id {record_id} not found"
        super().__init__(self.message)


class RecordAlreadyExists(Exception):
    def __init__(self, record_id: str):
        self.record_id = record_id
        self.message = f"Record with id {record_id} already exists"
        super().__init__(self.message)


class RecordNotActive(Exception):
    def __init__(self, record_id: str):
        self.record_id = record_id
        self.message = f"Record with id {record_id} is not active"
        super().__init__(self.message)


class DatabaseError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
