"""tests/test_endpoints.py

Integration tests for the FastAPI synthetic member generation endpoints.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    """Verify health check endpoint returns 200 OK."""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}


def test_generate_members_default_payload():
    """Verify generation with default request payload."""
    payload = {"num_records": 5}

    response = client.post("/api/v1/members/generate", json=payload)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["total_records"] == 5
    assert data["chaos_enabled"] is True
    assert isinstance(data["data"], list)
    assert len(data["data"]) == 5


def test_generate_members_deterministic_seed():
    """Verify deterministic generation using a fixed seed."""
    payload = {
        "num_records": 3,
        "seed": 42,
        "chaos": {
            "drift_rate": 0.0,
            "null_rate": 0.0,
            "outlier_rate": 0.0,
            "duplicate_rate": 0.0,
        },
    }

    res1 = client.post("/api/v1/members/generate", json=payload)
    res2 = client.post("/api/v1/members/generate", json=payload)

    assert res1.status_code == status.HTTP_200_OK
    assert res2.status_code == status.HTTP_200_OK
    assert res1.json()["data"] == res2.json()["data"]


def test_generate_members_with_chaos():
    """Verify that enabling chaos sets the chaos_enabled flag to True."""
    payload = {
        "num_records": 10,
        "seed": 123,
        "chaos": {
            "drift_rate": 0.5,
            "null_rate": 0.1,
            "outlier_rate": 0.0,
            "duplicate_rate": 0.0,
        },
    }

    response = client.post("/api/v1/members/generate", json=payload)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["chaos_enabled"] is True
    assert len(data["data"]) >= 10


@pytest.mark.parametrize(
    "invalid_payload, expected_loc",
    [
        ({"num_records": 0}, "num_records"),  # ge=1
        ({"num_records": 10001}, "num_records"),  # le=10000
        ({"num_records": 5, "chaos": {"drift_rate": 1.5}}, "drift_rate"),  # le=1.0
        ({"num_records": 5, "chaos": {"null_rate": -0.1}}, "null_rate"),  # ge=0.0 
    ],
)
def test_generate_members_validation_errors(invalid_payload, expected_loc):
    """Verify Pydantic input validation returns 422 Unprocessable Entity for out-of-bounds inputs."""
    response = client.post("/api/v1/members/generate", json=invalid_payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    errors = response.json().get("detail", [])
    field_locations = [error["loc"][-1] for error in errors]
    assert expected_loc in field_locations