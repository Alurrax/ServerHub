import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


pytestmark = pytest.mark.integration


def test_real_system_disks():
    response = client.get("/system/disks")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] >= 1
    assert len(data["disks"]) == data["count"]


def test_real_system_service_detail():
    response = client.get("/system/services/docker")

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "docker"
    assert data["unit"] == "docker.service"


def test_real_docker_containers():
    response = client.get("/system/docker/containers")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] >= 1


def test_real_docker_container_stats():
    response = client.get(
        "/system/docker/containers/serverhub-api/stats"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "serverhub-api"
    assert isinstance(data["cpu_percent"], float)
    assert isinstance(data["pids"], int)
