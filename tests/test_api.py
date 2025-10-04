from __future__ import annotations

from typing import Generator
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.main import app
from backend.models import candidate as _candidate  # noqa: F401 ensure model registration
from backend.models import job as _job  # noqa: F401 ensure model registration
from backend.models.database import Base, get_db

# Use in-memory SQLite with a static pool to share the same connection.
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db() -> Generator:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def test_job_crud_flow(client: TestClient) -> None:
    job_payload = {
        "title": "Backend Engineer",
        "company": "Acme",
        "description": "Build APIs",
        "location": "Remote",
        "skills": ["Python", "FastAPI"],
    }

    create_resp = client.post("/jobs", json=job_payload)
    assert create_resp.status_code == 201
    created_job = create_resp.json()
    job_id = created_job["id"]
    assert created_job["title"] == job_payload["title"]

    get_resp = client.get(f"/jobs/{job_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["company"] == job_payload["company"]

    update_resp = client.put(
        f"/jobs/{job_id}",
        json={"title": "Senior Backend Engineer"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["title"] == "Senior Backend Engineer"

    delete_resp = client.delete(f"/jobs/{job_id}")
    assert delete_resp.status_code == 204


def test_matching_endpoint_ranks_jobs(client: TestClient) -> None:
    job_payload = {
        "title": "Python Developer",
        "company": "Tech Corp",
        "description": "Create scalable services",
        "location": "Hybrid",
        "skills": ["Python", "FastAPI"],
    }
    job_resp = client.post("/jobs", json=job_payload)
    job_id = job_resp.json()["id"]

    candidate_payload = {
        "name": "Jane Doe",
        "skills": ["Python", "FastAPI"],
        "cv_text": "Experienced Python engineer with FastAPI expertise.",
    }
    candidate_resp = client.post("/candidates", json=candidate_payload)
    candidate_id = candidate_resp.json()["id"]

    match_resp = client.get(f"/match/candidate/{candidate_id}")
    assert match_resp.status_code == 200
    data = match_resp.json()

    assert data["candidate_id"] == candidate_id
    assert data["candidate_name"] == candidate_payload["name"]
    assert data["candidate_skills"] == sorted(candidate_payload["skills"], key=str.lower)

    results = data["results"]
    assert len(results) == 1
    top = results[0]
    assert top["job_id"] == job_id
    assert top["score"] == 1.0
    assert 0.0 <= top["semantic_score"] <= 1.0
    assert top["matched_skills"] == sorted(candidate_payload["skills"], key=str.lower)
    assert top["missing_skills"] == []
    assert top["candidate_extra_skills"] == []

def test_skill_gap_endpoint_aggregates_missing_skills(client: TestClient) -> None:
    job_one = {
        "title": "Backend Engineer",
        "company": "Acme",
        "description": "APIs",
        "location": "Remote",
        "skills": ["Python", "FastAPI", "SQL"],
    }
    job_two = {
        "title": "Platform Engineer",
        "company": "Beta",
        "description": "Infrastructure",
        "location": "Remote",
        "skills": ["Python", "Docker"],
    }
    client.post("/jobs", json=job_one)
    client.post("/jobs", json=job_two)

    candidate_payload = {
        "name": "Skill Gap Tester",
        "skills": ["Python"],
        "cv_text": "Python generalist",
    }
    candidate_resp = client.post("/candidates", json=candidate_payload)
    candidate_id = candidate_resp.json()["id"]

    resp = client.get(f"/match/candidate/{candidate_id}/skill-gap", params={"top_k": 10, "gap_limit": 10})
    assert resp.status_code == 200

    body = resp.json()
    assert body["candidate_id"] == candidate_id
    assert body["considered_jobs"] == 2

    gap_skills = {gap["skill"] for gap in body["gaps"]}
    assert gap_skills == {"FastAPI", "SQL", "Docker"}

    for gap in body["gaps"]:
        assert gap["demand_count"] == 1
        assert gap["demand_ratio"] == pytest.approx(0.5, abs=1e-4)
        assert gap["recommended_resources"]


def test_invalid_job_creation(client: TestClient) -> None:
    invalid_payload = {
        "title": "",  # Title is required
        "company": "Acme",
        "description": "Build APIs",
        "location": "Remote",
        "skills": ["Python", "FastAPI"],
    }

    response = client.post("/jobs", json=invalid_payload)
    assert response.status_code == 422


def test_nonexistent_job_retrieval(client: TestClient) -> None:
    response = client.get("/jobs/9999")  # Non-existent job ID
    assert response.status_code == 404


def test_unsupported_cv_upload(client: TestClient) -> None:
    file_content = b"This is a plain text file, not a PDF or DOCX."
    response = client.post(
        "/candidates/upload",
        files={"file": ("resume.txt", file_content, "text/plain")},
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.text
