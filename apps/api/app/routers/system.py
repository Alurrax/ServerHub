import os
import socket
import time
import httpx

import psutil
from fastapi import APIRouter, HTTPException


router = APIRouter(
    prefix="/system",
    tags=["system"],
)


def bytes_to_gb(value: int) -> float:
    return round(value / (1024**3), 2)


@router.get("/status")
def system_status():
    boot_time = psutil.boot_time()
    uptime_seconds = int(time.time() - boot_time)

    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    disk = psutil.disk_usage("/")

    load_1, load_5, load_15 = os.getloadavg()

    return {
        "host": {
            "hostname": os.environ["SERVER_HOSTNAME"],
            "cpu": {
                "percent": psutil.cpu_percent(interval=0.2),
                "logical_cores": psutil.cpu_count(logical=True),
                "physical_cores": psutil.cpu_count(logical=False),
                "load_1m": round(load_1, 2),
                "load_5m": round(load_5, 2),
                "load_15m": round(load_15, 2),
            },
            "memory": {
                "total_gb": bytes_to_gb(memory.total),
                "used_gb": bytes_to_gb(memory.used),
                "available_gb": bytes_to_gb(memory.available),
                "percent": memory.percent,
            },
            "swap": {
                "total_gb": bytes_to_gb(swap.total),
                "used_gb": bytes_to_gb(swap.used),
                "free_gb": bytes_to_gb(swap.free),
                "percent": swap.percent,
            },
            "disk": {
                "mount": "/",
                "total_gb": bytes_to_gb(disk.total),
                "used_gb": bytes_to_gb(disk.used),
                "free_gb": bytes_to_gb(disk.free),
                "percent": disk.percent,
            },
            "uptime_seconds": uptime_seconds,
        },
        "container": {
            "hostname": socket.gethostname(),
            "process_id": os.getpid(),
        },
    }

@router.get("/disks")
def system_disks():
    agent_url = os.environ["AGENT_URL"]

    try:
        response = httpx.get(
            f"{agent_url}/disks",
            timeout=3.0,
        )
        response.raise_for_status()

    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=503,
            detail="Host Agent unavailable",
        ) from exc

    return response.json()
