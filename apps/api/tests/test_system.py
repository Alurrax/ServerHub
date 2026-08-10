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

    assert 0 <= host["cpu_percent"] <= 100
    assert 0 <= host["memory_percent"] <= 100
    assert 0 <= host["disk_percent"] <= 100

    assert host["disk_free_gb"] >= 0
    assert host["uptime_seconds"] > 0

    assert container["hostname"]
    assert container["process_id"] > 0
