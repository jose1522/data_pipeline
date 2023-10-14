import pytest

from db.models import Department
from db.storage.department import DepartmentStorage
from db.storage.job import JobStorage


class TestJob:
    def test_post_job(self, client):
        payload = {
            "department": "Software Engineer",
        }
        response = client.post("/v1/department", json=payload)
        actual = response.json()
        assert response.status_code == 201
        assert actual["department"] == "Software Engineer"
        assert actual["id"] == 1

    def test_get_job(self, client, session):
        department = Department(department="Software Engineer")
        storage = DepartmentStorage(session=session)
        storage.create(department)
        session.commit()
        response = client.get("/v1/department/1")
        actual = response.json()
        assert response.status_code == 200
        assert actual["department"] == "Software Engineer"
        assert actual["id"] == 1

    def test_update_job(self, client, session):
        department = Department(department="Software Engineer")
        storage = DepartmentStorage(session=session)
        storage.create(department)
        session.commit()
        expected_pk = department.id
        payload = {
            "department": "Software Engineer II",
        }
        response = client.patch("/v1/department/1", json=payload)
        actual = response.json()
        assert response.status_code == 200
        assert actual["department"] == "Software Engineer II"
        assert actual["id"] == expected_pk

    def test_soft_delete_job(self, client, session):
        department = Department(department="Software Engineer")
        storage = DepartmentStorage(session=session)
        storage.create(department)
        session.commit()
        response = client.delete("/v1/department/1")
        assert response.status_code == 204
        assert not storage.exists(1)
        assert storage.exists(1, is_active=False)

    def test_hard_delete_job(self, client, session):
        department = Department(department="Software Engineer")
        storage = DepartmentStorage(session=session)
        storage.create(department)
        session.commit()
        response = client.delete("/v1/department/1", headers={"X-Soft-Delete": "False"})
        assert response.status_code == 204
        assert not storage.exists(1, is_active=False)

    def test_get_job_not_found(self, client):
        response = client.get("/v1/department/1")
        assert response.status_code == 404

    def test_update_job_not_found(self, client):
        payload = {
            "department": "Software Engineer II",
        }
        response = client.patch("/v1/department/1", json=payload)
        assert response.status_code == 404

    def test_delete_job_not_found(self, client):
        response = client.delete("/v1/department/1")
        assert response.status_code == 404

    def test_get_soft_deleted(self, client, session):
        department = Department(department="Software Engineer")
        storage = DepartmentStorage(session=session)
        storage.create(department)
        session.commit()
        storage.delete(1)
        session.commit()
        response = client.get("/v1/department/1")
        assert response.status_code == 410

    def test_insert_soft_deleted(self, client, session):
        department = Department(department="Software Engineer")
        storage = DepartmentStorage(session=session)
        storage.create(department)
        session.commit()
        storage.delete(1)
        session.commit()
        payload = {
            "department": "Software Engineer",
        }
        response = client.post("/v1/department", json=payload)
        # API is expected to upsert and reactivate the record
        assert response.status_code == 201

    def test_update_soft_deleted(self, client, session):
        department = Department(department="Software Engineer")
        storage = DepartmentStorage(session=session)
        storage.create(department)
        session.commit()
        storage.delete(1)
        session.commit()
        payload = {
            "department": "Software Engineer II",
            "is_active": True,
        }
        response = client.patch("/v1/department/1", json=payload)
        assert response.status_code == 410

    def test_create_duplicate(self, client, session):
        department = Department(department="Software Engineer")
        storage = DepartmentStorage(session=session)
        storage.create(department)
        session.commit()
        payload = {
            "department": "Software Engineer",
        }
        response = client.post("/v1/department", json=payload)
        assert response.status_code == 201

    def test_update_duplicate(self, client, session):
        department = Department(department="Software Engineer")
        storage = DepartmentStorage(session=session)
        storage.create(department)
        session.commit()
        job2 = Department(department="Software Engineer II")
        storage.create(job2)
        session.commit()
        payload = {
            "department": "Software Engineer II",
        }
        response = client.patch("/v1/department/1", json=payload)
        assert response.status_code == 500

    def test_bulk_insert(self, client):
        departments = {
            "departments": [{"department": f"department {i}"} for i in range(1000)]
        }

        # Send request to the endpoint
        response = client.post("/v1/department/bulk", json=departments)

        # Check the response status code and data
        assert response.status_code == 201

    def test_bulk_insert_too_many(self, client):
        jobs_data = {"jobs": [{"department": f"Department {i}"} for i in range(1001)]}

        # Send request to the endpoint
        response = client.post("/v1/department/bulk", json=jobs_data)

        # Check the response status code and data
        assert response.status_code == 422

    @pytest.mark.parametrize("limit", [1, 10, 100, 1000])
    def test_get_all_departments(self, limit, client, session):
        departments = {"departments": [{"department": f"Department {i}"} for i in range(limit)]}
        storage = DepartmentStorage(session=session)
        storage.bulk_upsert(departments["departments"])
        session.commit()

        # Send request to the endpoint
        response = client.get(f"/v1/department/?limit={limit}")

        # Check the response status code and data
        assert response.status_code == 200
        assert len(response.json()) == limit
        for i in range(limit):
            assert response.json()[i]["department"] == f"Department {i}"

    def test_get_all_departments_empty(self, client, session):
        # Send request to the endpoint
        response = client.get("/v1/job/")

        # Check the response status code and data
        assert response.status_code == 200
        assert len(response.json()) == 0

    def test_get_all_soft_deleted(self, client, session):
        department = Department(department="Department")
        storage = JobStorage(session=session)
        storage.create(department)
        session.commit()
        storage.delete(1)
        session.commit()
        response = client.get("/v1/department/")
        assert response.status_code == 200
        assert len(response.json()) == 0
