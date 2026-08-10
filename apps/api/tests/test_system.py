from fastapi.testclient import TestClient

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

def test_system_disks():
    response = client.get("/system/disks")

    assert response.status_code == 200

    data = response.json()

    assert "disks" in data
    assert "count" in data

    assert data["count"] >= 1
    assert len(data["disks"]) == data["count"]

    disk_names = [
        disk["name"]
        for disk in data["disks"]
    ]

    assert "sda" in disk_names
    assert "nvme0n1" in disk_names

def test_system_service_detail():
    response = client.get("/system/services/docker")

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "docker"
    assert data["unit"] == "docker.service"

    assert "load" in data
    assert "active" in data
    assert "sub" in data
    assert "description" in data


def test_system_service_not_found():
    response = client.get(
        "/system/services/serverhub-service-that-does-not-exist"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Service not found"

def test_system_service_restart():
    response = client.post(
        "/system/services/smbd/restart"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["service"] == "smbd"
    assert data["action"] == "restart"
    assert data["status"] == "success"


def test_system_service_restart_forbidden():
    response = client.post(
        "/system/services/ssh/restart"
    )

    assert response.status_code == 403
    assert (
        response.json()["detail"]
        == "Service is not managed by ServerHub"
    )
