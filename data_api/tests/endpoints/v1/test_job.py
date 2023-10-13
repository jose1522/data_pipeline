from db.models import Job
from db.storage.job import JobStorage


class TestJob:
    def test_post_job(self, client):
        payload = {
            "job": "Software Engineer",
        }
        response = client.post("/v1/job", json=payload)
        actual = response.json()
        assert response.status_code == 201
        assert actual["job"] == "Software Engineer"
        assert actual["id"] == 1

    def test_get_job(self, client, session):
        job = Job(job="Software Engineer")
        storage = JobStorage(session=session)
        storage.create(job)
        session.commit()
        response = client.get("/v1/job/1")
        actual = response.json()
        assert response.status_code == 200
        assert actual["job"] == "Software Engineer"
        assert actual["id"] == 1

    def test_update_job(self, client, session):
        job = Job(job="Software Engineer")
        storage = JobStorage(session=session)
        storage.create(job)
        session.commit()
        expected_pk = job.id
        payload = {
            "job": "Software Engineer II",
        }
        response = client.patch("/v1/job/1", json=payload)
        actual = response.json()
        assert response.status_code == 200
        assert actual["job"] == "Software Engineer II"
        assert actual["id"] == expected_pk

    def test_soft_delete_job(self, client, session):
        job = Job(job="Software Engineer")
        storage = JobStorage(session=session)
        storage.create(job)
        session.commit()
        response = client.delete("/v1/job/1")
        assert response.status_code == 204
        assert not storage.read(1)
        assert storage.exists(1, is_active=False)

    def test_hard_delete_job(self, client, session):
        job = Job(job="Software Engineer")
        storage = JobStorage(session=session)
        storage.create(job)
        session.commit()
        response = client.delete("/v1/job/1?soft_delete=true")
        assert response.status_code == 204
        assert not storage.read(1)
        assert not storage.exists(1)

    def test_get_job_not_found(self, client):
        response = client.get("/v1/job/1")
        assert response.status_code == 404
        assert response.json() == {"detail": "Job not found"}

    def test_update_job_not_found(self, client):
        payload = {
            "job": "Software Engineer II",
        }
        response = client.patch("/v1/job/1", json=payload)
        assert response.status_code == 404
        assert response.json() == {"detail": "Job not found"}

    def test_delete_job_not_found(self, client):
        response = client.delete("/v1/job/1")
        assert response.status_code == 404
        assert response.json() == {"detail": "Job not found"}

    def test_get_soft_deleted(self, client, session):
        job = Job(job="Software Engineer")
        storage = JobStorage(session=session)
        storage.create(job)
        session.commit()
        storage.delete(1)
        session.commit()
        response = client.get("/v1/job/1")
        assert response.status_code == 204

    def test_insert_soft_deleted(self, client, session):
        job = Job(job="Software Engineer")
        storage = JobStorage(session=session)
        storage.create(job)
        session.commit()
        storage.delete(1)
        session.commit()
        payload = {
            "job": "Software Engineer",
        }
        response = client.post("/v1/job", json=payload)
        assert response.status_code == 201

    def test_update_soft_deleted(self, client, session):
        job = Job(job="Software Engineer")
        storage = JobStorage(session=session)
        storage.create(job)
        session.commit()
        storage.delete(1)
        session.commit()
        payload = {
            "job": "Software Engineer II",
            "is_active": True,
        }
        response = client.patch("/v1/job/1", json=payload)
        assert response.status_code == 404
        assert response.json() == {"detail": "Job not found"}