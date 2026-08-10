import json
import socket
import subprocess

from fastapi import FastAPI, HTTPException


app = FastAPI(
    title="ServerHub Host Agent",
    version="0.1.0",
)

MANAGED_SERVICES = {
    "docker": "docker.service",
    "smbd": "smbd.service",
}

def validate_managed_service(name: str) -> str:
    unit = MANAGED_SERVICES.get(name)

    if unit is None:
        raise HTTPException(
            status_code=403,
            detail="Service is not managed by ServerHub",
        )

    return unit

def bytes_to_gib(value: int | None) -> float | None:
    if value is None:
        return None

    return round(value / (1024**3), 2)


def get_disks() -> dict:
    command = [
        "lsblk",
        "--json",
        "--bytes",
        "--output",
        "NAME,PATH,TYPE,FSTYPE,LABEL,SIZE,FSAVAIL,FSUSE%,MOUNTPOINTS",
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
    )

    data = json.loads(result.stdout)

    disks = []

    for device in data["blockdevices"]:
        if device["type"] != "disk":
            continue

        partitions = []

        for partition in device.get("children", []):
            partitions.append(
                {
                    "name": partition["name"],
                    "path": partition["path"],
                    "filesystem": partition["fstype"],
                    "label": partition["label"],
                    "size_gib": bytes_to_gib(partition["size"]),
                    "available_gib": bytes_to_gib(
                        partition["fsavail"]
                    ),
                    "used_percent": partition["fsuse%"],
                    "mountpoints": partition["mountpoints"],
                }
            )

        disks.append(
            {
                "name": device["name"],
                "path": device["path"],
                "size_gib": bytes_to_gib(device["size"]),
                "partitions": partitions,
            }
        )

    return {
        "disks": disks,
        "count": len(disks),
    }

def get_services() -> dict:
    command = [
        "systemctl",
        "list-units",
        "--type=service",
        "--all",
        "--no-legend",
        "--no-pager",
        "--plain",
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
    )

    services = []

    for line in result.stdout.splitlines():
        parts = line.split(None, 4)

        if len(parts) < 4:
            continue

        unit = parts[0]
        load = parts[1]
        active = parts[2]
        sub = parts[3]
        description = parts[4] if len(parts) == 5 else ""

        services.append(
            {
                "unit": unit,
                "name": unit.removesuffix(".service"),
                "load": load,
                "active": active,
                "sub": sub,
                "description": description,
            }
        )

    return {
        "services": services,
        "count": len(services),
    }

def get_service(name: str) -> dict | None:
    services = get_services()["services"]

    for service in services:
        if service["name"] == name:
            return service

    return None

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "hostname": socket.gethostname(),
    }


@app.get("/disks")
def disks():
    return get_disks()

@app.get("/services")
def services():
    return get_services()

@app.get("/services/{name}")
def service_detail(name: str):
    service = get_service(name)

    if service is None:
        raise HTTPException(
            status_code=404,
            detail="Service not found",
        )

    return service

@app.post("/services/{name}/restart")
def restart_service(name: str):
    unit = validate_managed_service(name)

    try:
        subprocess.run(
            ["sudo", "systemctl", "restart", unit],
            capture_output=True,
            text=True,
            check=True,
            timeout=15,
        )

    except subprocess.CalledProcessError as exc:
        raise HTTPException(
            status_code=500,
            detail=exc.stderr.strip() or "Failed to restart service",
        ) from exc

    except subprocess.TimeoutExpired as exc:
        raise HTTPException(
            status_code=504,
            detail="Service restart timed out",
        ) from exc

    return {
        "service": name,
        "action": "restart",
        "status": "success",
    }
