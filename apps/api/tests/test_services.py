from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_services_crud():
    # Generamos un nombre único para poder ejecutar el test muchas veces.
    service_name = f"test-service-{uuid4().hex[:8]}"

    # CREATE
    response = client.post(
        "/services",
        json={
            "name": service_name,
            "status": "testing",
            "description": "Servicio temporal creado por pytest",
        },
    )

    assert response.status_code == 200

    created = response.json()

    assert created["name"] == service_name
    assert created["status"] == "testing"
    assert created["description"] == "Servicio temporal creado por pytest"

    service_id = created["id"]

    # READ ONE
    response = client.get(f"/services/{service_id}")

    assert response.status_code == 200

    service = response.json()

    assert service["id"] == service_id
    assert service["name"] == service_name

    # UPDATE
    response = client.patch(
        f"/services/{service_id}",
        json={
            "status": "stopped",
            "description": "Servicio modificado por pytest",
        },
    )

    assert response.status_code == 200

    updated = response.json()

    assert updated["status"] == "stopped"
    assert updated["description"] == "Servicio modificado por pytest"

    # READ ALL
    response = client.get("/services")

    assert response.status_code == 200

    services = response.json()

    assert any(
        service["id"] == service_id
        for service in services
    )

    # DELETE
    response = client.delete(f"/services/{service_id}")

    assert response.status_code == 204

    # CONFIRMAR ELIMINACIÓN
    response = client.get(f"/services/{service_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Service not found"
