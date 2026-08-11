import json
import socket
import subprocess

from fastapi import FastAPI, HTTPException


app = FastAPI(
    title="ServerHub Host Agent",
    version="0.1.0",
)


MANAGED_SERVICES = {
    "docker": {
        "unit": "docker.service",
        "actions": {"restart"},
    },
    "smbd": {
        "unit": "smbd.service",
        "actions": {"start", "stop", "restart"},
    },
}


def validate_service_action(name: str, action: str) -> str:
    service = MANAGED_SERVICES.get(name)

    if service is None:
        raise HTTPException(
            status_code=403,
            detail="Service is not managed by ServerHub",
        )

    if action not in service["actions"]:
        raise HTTPException(
            status_code=403,
            detail=f"Action '{action}' is not allowed for service '{name}'",
        )

    return service["unit"]


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


def run_service_action(name: str, action: str) -> dict:
    unit = validate_service_action(name, action)

    try:
        subprocess.run(
            ["sudo", "systemctl", action, unit],
            capture_output=True,
            text=True,
            check=True,
            timeout=15,
        )

    except subprocess.CalledProcessError as exc:
        raise HTTPException(
            status_code=500,
            detail=exc.stderr.strip() or f"Failed to {action} service",
        ) from exc

    except subprocess.TimeoutExpired as exc:
        raise HTTPException(
            status_code=504,
            detail=f"Service {action} timed out",
        ) from exc

    return {
        "service": name,
        "action": action,
        "status": "success",
    }

def get_docker_containers() -> dict:
    command = [
        "docker",
        "ps",
        "-a",
        "--format",
        "{{json .}}",
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )

    except subprocess.CalledProcessError as exc:
        raise HTTPException(
            status_code=500,
            detail=exc.stderr.strip() or "Failed to read Docker containers",
        ) from exc

    except subprocess.TimeoutExpired as exc:
        raise HTTPException(
            status_code=504,
            detail="Docker command timed out",
        ) from exc

    containers = []

    for line in result.stdout.splitlines():
        if not line.strip():
            continue

        item = json.loads(line)

        containers.append(
            {
                "id": item.get("ID"),
                "name": item.get("Names"),
                "image": item.get("Image"),
                "status": item.get("Status"),
                "state": item.get("State"),
                "ports": item.get("Ports"),
                "created_at": item.get("CreatedAt"),
            }
        )

    return {
        "containers": containers,
        "count": len(containers),
    }

def get_docker_container(name: str) -> dict:
    try:
        result = subprocess.run(
            ["docker", "inspect", name],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )

    except subprocess.CalledProcessError as exc:
        raise HTTPException(
            status_code=404,
            detail="Container not found",
        ) from exc

    except subprocess.TimeoutExpired as exc:
        raise HTTPException(
            status_code=504,
            detail="Docker command timed out",
        ) from exc

    data = json.loads(result.stdout)[0]

    state = data.get("State", {})
    config = data.get("Config", {})
    network_settings = data.get("NetworkSettings", {})

    networks = {}

    for network_name, network in network_settings.get(
        "Networks", {}
    ).items():
        networks[network_name] = {
            "ip_address": network.get("IPAddress"),
            "gateway": network.get("Gateway"),
            "mac_address": network.get("MacAddress"),
        }

    return {
        "id": data.get("Id"),
        "name": data.get("Name", "").lstrip("/"),
        "image": config.get("Image"),
        "status": state.get("Status"),
        "running": state.get("Running"),
        "started_at": state.get("StartedAt"),
        "finished_at": state.get("FinishedAt"),
        "restart_count": data.get("RestartCount"),
        "platform": data.get("Platform"),
        "networks": networks,
        "ports": network_settings.get("Ports"),
    }

def get_docker_container_stats(name: str) -> dict:
    command = [
        "docker",
        "stats",
        name,
        "--no-stream",
        "--format",
        "{{json .}}",
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )

    except subprocess.CalledProcessError as exc:
        error = exc.stderr.strip()

        if "No such container" in error:
            raise HTTPException(
                status_code=404,
                detail="Container not found",
            ) from exc

        raise HTTPException(
            status_code=500,
            detail=error or "Failed to read container stats",
        ) from exc

    except subprocess.TimeoutExpired as exc:
        raise HTTPException(
            status_code=504,
            detail="Docker stats timed out",
        ) from exc

    if not result.stdout.strip():
        raise HTTPException(
            status_code=404,
            detail="Container not found",
        )

    data = json.loads(result.stdout)

    memory_usage = data.get("MemUsage", "")
    memory_parts = [
        part.strip()
        for part in memory_usage.split("/")
    ]

    return {
        "name": data.get("Name"),
        "cpu_percent": float(
            data.get("CPUPerc", "0%").rstrip("%")
        ),
        "memory": {
            "usage": (
                memory_parts[0]
                if len(memory_parts) >= 1
                else None
            ),
            "limit": (
                memory_parts[1]
                if len(memory_parts) >= 2
                else None
            ),
            "percent": float(
                data.get("MemPerc", "0%").rstrip("%")
            ),
        },
        "network_io": data.get("NetIO"),
        "block_io": data.get("BlockIO"),
        "pids": int(data.get("PIDs", 0)),
    }


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


@app.post("/services/{name}/start")
def start_service(name: str):
    return run_service_action(name, "start")


@app.post("/services/{name}/stop")
def stop_service(name: str):
    return run_service_action(name, "stop")


@app.post("/services/{name}/restart")
def restart_service(name: str):
    return run_service_action(name, "restart")

@app.get("/docker/containers")
def docker_containers():
    return get_docker_containers()

@app.get("/docker/containers/{name}")
def docker_container_detail(name: str):
    return get_docker_container(name)

@app.get("/docker/containers/{name}/stats")
def docker_container_stats(name: str):
    return get_docker_container_stats(name)
