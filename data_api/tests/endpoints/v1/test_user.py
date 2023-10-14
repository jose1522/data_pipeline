from db.storage.department import DepartmentStorage
from db.storage.job import JobStorage


class TestUser:
    def _init_fks(self, session):
        job_storage = JobStorage(session=session)
        department_storage = DepartmentStorage(session=session)
        job_storage.bulk_upsert([{"job": f"Job {i}"} for i in range(10)])
        department_storage.bulk_upsert(
            [{"department": f"Department {i}"} for i in range(10)]
        )
        session.commit()

    def test_post_user(self, client, session):
        self._init_fks(session)
        payload = {
            "name": "John Doe",
            "datetime": "2020-01-01T00:00:00",
            "job_id": 1,
            "department_id": 1,
        }
        response = client.post("/v1/user/", json=payload)
        assert response.status_code == 201
        assert response.json()["name"] == "John Doe"
        assert response.json()["job"]["id"] == 1
        assert response.json()["department"]["id"] == 1

    def test_post_user_wrong_fk(self, client, session):
        payload = {
            "name": "John Doe",
            "datetime": "2020-01-01T00:00:00",
            "job_id": 1,
            "department_id": 100,
        }
        response = client.post("/v1/user/", json=payload)
        assert response.status_code == 400
