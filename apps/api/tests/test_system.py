from fastapi.testclient import TestClient
from unittest.mock import Mock
from app.main import app


client = TestClient(app)


def test_system_status():
    response = client.get("/system/status")

    assert response.status_code == 200

    data = response.json()

    assert "host" in data
    assert "container" in data

    host = data["host"]
    container = data["container"]

    assert host["hostname"] == "LenoPC"

    # CPU
    assert "cpu" in host
    assert 0 <= host["cpu"]["percent"] <= 100
    assert host["cpu"]["logical_cores"] > 0
    assert host["cpu"]["physical_cores"] > 0
    assert host["cpu"]["load_1m"] >= 0
    assert host["cpu"]["load_5m"] >= 0
    assert host["cpu"]["load_15m"] >= 0

    # Memoria
    assert "memory" in host
    assert host["memory"]["total_gb"] > 0
    assert host["memory"]["used_gb"] >= 0
    assert host["memory"]["available_gb"] >= 0
    assert 0 <= host["memory"]["percent"] <= 100

    # Swap
    assert "swap" in host
    assert host["swap"]["total_gb"] >= 0
    assert host["swap"]["used_gb"] >= 0
    assert host["swap"]["free_gb"] >= 0
    assert 0 <= host["swap"]["percent"] <= 100

    # Disco
    assert "disk" in host
    assert host["disk"]["mount"] == "/"
    assert host["disk"]["total_gb"] > 0
    assert host["disk"]["used_gb"] >= 0
    assert host["disk"]["free_gb"] >= 0
    assert 0 <= host["disk"]["percent"] <= 100

    # Uptime
    assert host["uptime_seconds"] > 0

    # Contenedor
    assert container["hostname"]
    assert container["process_id"] > 0

def test_system_disks(monkeypatch):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "disks": [
            {
                "name": "sda",
                "path": "/dev/sda",
                "size_gib": 931.51,
                "partitions": [],
            },
            {
                "name": "nvme0n1",
                "path": "/dev/nvme0n1",
                "size_gib": 119.24,
                "partitions": [],
            },
        ],
        "count": 2,
    }
    mock_response.raise_for_status.return_value = None

    monkeypatch.setattr(
        "app.routers.system.httpx.get",
        lambda *args, **kwargs: mock_response,
    )

    response = client.get("/system/disks")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 2

    disk_names = [
        disk["name"]
        for disk in data["disks"]
    ]

    assert "sda" in disk_names
    assert "nvme0n1" in disk_names

def test_system_service_detail(monkeypatch):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "unit": "docker.service",
        "name": "docker",
        "load": "loaded",
        "active": "active",
        "sub": "running",
        "description": "Docker Application Container Engine",
    }
    mock_response.raise_for_status.return_value = None

    monkeypatch.setattr(
        "app.routers.system.httpx.get",
        lambda *args, **kwargs: mock_response,
    )

    response = client.get("/system/services/docker")

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "docker"
    assert data["unit"] == "docker.service"

def test_system_service_not_found(monkeypatch):
    mock_response = Mock()
    mock_response.status_code = 404

    monkeypatch.setattr(
        "app.routers.system.httpx.get",
        lambda *args, **kwargs: mock_response,
    )

    response = client.get(
        "/system/services/serverhub-service-that-does-not-exist"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Service not found"

def test_system_service_restart(monkeypatch):
    mock_response = Mock()

    mock_response.status_code = 200
    mock_response.json.return_value = {
        "service": "smbd",
        "action": "restart",
        "status": "success",
    }

    mock_response.raise_for_status.return_value = None

    def mock_post(*args, **kwargs):
        return mock_response

    monkeypatch.setattr(
        "app.routers.system.httpx.post",
        mock_post,
    )

    response = client.post(
        "/system/services/smbd/restart"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["service"] == "smbd"
    assert data["action"] == "restart"
    assert data["status"] == "success"


def test_system_service_restart_forbidden(monkeypatch):
    mock_response = Mock()

    mock_response.status_code = 403
    mock_response.json.return_value = {
        "detail": "Service is not managed by ServerHub"
    }

    def mock_post(*args, **kwargs):
        return mock_response

    monkeypatch.setattr(
        "app.routers.system.httpx.post",
        mock_post,
    )

    response = client.post(
        "/system/services/ssh/restart"
    )

    assert response.status_code == 403
    assert (
        response.json()["detail"]
        == "Service is not managed by ServerHub"
    )

def test_system_docker_containers(monkeypatch):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "containers": [
            {
                "name": "serverhub-api",
                "state": "running",
            },
            {
                "name": "serverhub-db",
                "state": "running",
            },
        ],
        "count": 2,
    }
    mock_response.raise_for_status.return_value = None

    monkeypatch.setattr(
        "app.routers.system.httpx.get",
        lambda *args, **kwargs: mock_response,
    )

    response = client.get("/system/docker/containers")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 2

    names = [
        container["name"]
        for container in data["containers"]
    ]

    assert "serverhub-api" in names
    assert "serverhub-db" in names

def test_system_docker_container_detail(monkeypatch):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "name": "serverhub-api",
        "image": "serverhub-api",
        "status": "running",
        "running": True,
        "restart_count": 0,
        "networks": {},
        "ports": {},
    }
    mock_response.raise_for_status.return_value = None

    monkeypatch.setattr(
        "app.routers.system.httpx.get",
        lambda *args, **kwargs: mock_response,
    )

    response = client.get(
        "/system/docker/containers/serverhub-api"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "serverhub-api"
    assert data["running"] is True

def test_system_docker_container_not_found(monkeypatch):
    mock_response = Mock()
    mock_response.status_code = 404

    monkeypatch.setattr(
        "app.routers.system.httpx.get",
        lambda *args, **kwargs: mock_response,
    )

    response = client.get(
        "/system/docker/containers/no-existe"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Container not found"

def test_system_docker_container_stats(monkeypatch):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "name": "serverhub-api",
        "cpu_percent": 0.31,
        "memory": {
            "usage": "105.9MiB",
            "limit": "7.119GiB",
            "percent": 1.45,
        },
        "network_io": "717kB / 340kB",
        "block_io": "5.19MB / 3.02MB",
        "pids": 5,
    }
    mock_response.raise_for_status.return_value = None

    monkeypatch.setattr(
        "app.routers.system.httpx.get",
        lambda *args, **kwargs: mock_response,
    )

    response = client.get(
        "/system/docker/containers/serverhub-api/stats"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["cpu_percent"], float)
    assert isinstance(data["memory"]["percent"], float)
    assert isinstance(data["pids"], int)


def test_system_docker_container_stats_not_found(monkeypatch):
    mock_response = Mock()
    mock_response.status_code = 404

    monkeypatch.setattr(
        "app.routers.system.httpx.get",
        lambda *args, **kwargs: mock_response,
    )

    response = client.get(
        "/system/docker/containers/no-existe/stats"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Container not found"

def test_system_docker_container_restart(monkeypatch):
    mock_response = Mock()

    mock_response.status_code = 200
    mock_response.json.return_value = {
        "container": "serverhub-db",
        "action": "restart",
        "status": "success",
    }

    mock_response.raise_for_status.return_value = None

    def mock_post(*args, **kwargs):
        return mock_response

    monkeypatch.setattr(
        "app.routers.system.httpx.post",
        mock_post,
    )

    response = client.post(
        "/system/docker/containers/serverhub-db/restart"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["container"] == "serverhub-db"
    assert data["action"] == "restart"
    assert data["status"] == "success"

def test_system_docker_container_restart_forbidden(monkeypatch):
    mock_response = Mock()

    mock_response.status_code = 403
    mock_response.json.return_value = {
        "detail": "Container is not managed by ServerHub"
    }

    def mock_post(*args, **kwargs):
        return mock_response

    monkeypatch.setattr(
        "app.routers.system.httpx.post",
        mock_post,
    )

    response = client.post(
        "/system/docker/containers/no-existe/restart"
    )

    assert response.status_code == 403
    assert (
        response.json()["detail"]
        == "Container is not managed by ServerHub"
    )
