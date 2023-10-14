import pytest

from db.models import User
from db.storage.department import DepartmentStorage
from db.storage.job import JobStorage
from db.storage.user import UserStorage


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

    def test_post_user_bad_fk(self, client, session):
        payload = {
            "name": "John Doe",
            "datetime": "2020-01-01T00:00:00",
            "job_id": 1,
            "department_id": 100,
        }
        response = client.post("/v1/user/", json=payload)
        assert response.status_code == 400

    def test_post_user_soft_deleted_fk(self, client, session):
        self._init_fks(session)
        job_storage = JobStorage(session=session)
        job_storage.delete(1)
        session.commit()
        payload = {
            "name": "John Doe",
            "datetime": "2020-01-01T00:00:00",
            "job_id": 1,
            "department_id": 1,
        }
        response = client.post("/v1/user/", json=payload)
        assert response.status_code == 400

    @pytest.mark.parametrize("limit", [1, 10, 100, 1000])
    def test_get_many_users(self, client, session, limit):
        self._init_fks(session)
        users = [
            User(
                **{
                    "name": f"John Doe {i}",
                    "datetime": "2020-01-01T00:00:00",
                    "job_id": 1,
                    "department_id": 1,
                }
            )
            for i in range(limit)
        ]
        storage = UserStorage(session=session)
        for user in users:
            storage.create(user)
        session.commit()
        response = client.get(f"/v1/user/?limit={limit}")
        assert response.status_code == 200
        assert len(response.json()) == limit
        for i in range(limit):
            assert response.json()[i]["name"] == f"John Doe {i}"
            assert response.json()[i]["job"]["id"] == 1
            assert response.json()[i]["department"]["id"] == 1

    def test_get_user(self, client, session):
        self._init_fks(session)
        users_storage = UserStorage(session=session)
        user = User(
            name="John Doe", datetime="2020-01-01T00:00:00", job_id=1, department_id=1
        )
        users_storage.create(user)
        session.commit()
        response = client.get("/v1/user/1")
        assert response.status_code == 200
        assert response.json()["name"] == "John Doe"
        assert response.json()["job"]["id"] == 1
        assert response.json()["department"]["id"] == 1

    def test_get_user_not_found(self, client):
        response = client.get("/v1/user/1")
        assert response.status_code == 404

    def test_get_soft_deleted_fk(self, client, session):
        self._init_fks(session)
        users_storage = UserStorage(session=session)
        user = User(
            name="John Doe", datetime="2020-01-01T00:00:00", job_id=1, department_id=1
        )
        users_storage.create(user)
        session.commit()
        job_storage = JobStorage(session=session)
        job_storage.delete(1)
        session.commit()
        response = client.get("/v1/user/1")
        assert response.status_code == 200
        assert response.json()["job"] is None

    def test_get_hard_deleted_fk(self, client, session):
        self._init_fks(session)
        users_storage = UserStorage(session=session)
        user = User(
            name="John Doe", datetime="2020-01-01T00:00:00", job_id=1, department_id=1
        )
        users_storage.create(user)
        session.commit()
        job_storage = JobStorage(session=session)
        job_storage.delete(1, soft_delete=False)
        session.commit()
        response = client.get("/v1/user/1")
        assert response.status_code == 404

    def test_create_deleted_fk(self, client, session):
        self._init_fks(session)
        job_storage = JobStorage(session=session)
        job_storage.delete(1)
        session.commit()
        payload = {
            "name": "John Doe",
            "datetime": "2020-01-01T00:00:00",
            "job_id": 1,
            "department_id": 1,
        }
        response = client.post("/v1/user/", json=payload)
        assert response.status_code == 400

    def test_soft_delete_user(self, client, session):
        self._init_fks(session)
        users_storage = UserStorage(session=session)
        user = User(
            name="John Doe", datetime="2020-01-01T00:00:00", job_id=1, department_id=1
        )
        users_storage.create(user)
        session.commit()
        response = client.delete("/v1/user/1")
        assert response.status_code == 204
        assert not users_storage.exists(1)
        assert users_storage.exists(1, is_active=False)
        job_storage = JobStorage(session=session)
        assert job_storage.exists(1)

    def test_hard_delete_user(self, client, session):
        self._init_fks(session)
        users_storage = UserStorage(session=session)
        user = User(
            name="John Doe", datetime="2020-01-01T00:00:00", job_id=1, department_id=1
        )
        users_storage.create(user)
        session.commit()
        response = client.delete("/v1/user/1", headers={"X-Soft-Delete": "False"})
        assert response.status_code == 204
        assert not users_storage.exists(1)
        assert not users_storage.exists(1, is_active=False)
        job_storage = JobStorage(session=session)
        assert job_storage.exists(1)

    def test_update_user(self, client, session):
        self._init_fks(session)
        users_storage = UserStorage(session=session)
        user = User(
            name="John Doe", datetime="2020-01-01T00:00:00", job_id=1, department_id=1
        )
        users_storage.create(user)
        session.commit()
        payload = {
            "name": "Jane Doe",
            "datetime": "2020-01-01T00:00:00",
            "job_id": 2,
            "department_id": 2,
        }
        response = client.patch("/v1/user/1", json=payload)
        assert response.status_code == 200
        assert response.json()["name"] == "Jane Doe"
        assert response.json()["job"]["id"] == 2
        assert response.json()["department"]["id"] == 2

    @pytest.mark.parametrize("count", [1, 10])
    def test_bulk_create_users(self, client, session, count):
        self._init_fks(session)
        storage = UserStorage(session=session)
        payload = [
            {
                "name": f"John Doe {i}",
                "datetime": "2020-01-01T00:00:00",
                "job_id": 1,
                "department_id": 1,
            }
            for i in range(count)
        ]
        response = client.post("/v1/user/bulk", json=payload)
        assert response.status_code == 201
        assert len(storage.all(limit=count + 1)) == count

    def test_bulk_create_users_bad_fk(self, client, session):
        self._init_fks(session)
        payload = [
            {
                "name": f"John Doe {i}",
                "datetime": "2020-01-01T00:00:00",
                "job_id": 1,
                "department_id": 100,
            }
            for i in range(10)
        ]
        response = client.post("/v1/user/bulk", json=payload)
        assert response.status_code == 400

    def test_bulk_create_duplicate_users(self, client, session):
        self._init_fks(session)
        payload = [
            {
                "name": "John Doe",
                "datetime": "2020-01-01T00:00:00",
                "job_id": 1,
                "department_id": 1,
            }
            for i in range(10)
        ]
        response = client.post("/v1/user/bulk", json=payload)
        assert response.status_code == 400

    def test_update_user_bad_fk(self, client, session):
        self._init_fks(session)
        users_storage = UserStorage(session=session)
        user = User(
            name="John Doe", datetime="2020-01-01T00:00:00", job_id=1, department_id=1
        )
        users_storage.create(user)
        session.commit()
        payload = {
            "name": "Jane Doe",
            "datetime": "2020-01-01T00:00:00",
            "job_id": 2,
            "department_id": 100,
        }
        response = client.patch("/v1/user/1", json=payload)
        assert response.status_code == 400

    def test_update_user_not_found(self, client, session):
        self._init_fks(session)
        payload = {
            "name": "Jane Doe",
            "datetime": "2020-01-01T00:00:00",
            "job_id": 1,
            "department_id": 1,
        }
        response = client.patch("/v1/user/1", json=payload)
        assert response.status_code == 404

    def test_update_user_soft_deleted_fk(self, client, session):
        self._init_fks(session)
        users_storage = UserStorage(session=session)
        user = User(
            name="John Doe", datetime="2020-01-01T00:00:00", job_id=1, department_id=1
        )
        users_storage.create(user)
        session.commit()
        job_storage = JobStorage(session=session)
        job_storage.delete(1)
        session.commit()
        payload = {
            "name": "Jane Doe",
            "datetime": "2020-01-01T00:00:00",
            "job_id": 1,
            "department_id": 1,
        }
        response = client.patch("/v1/user/1", json=payload)
        assert response.status_code == 400
