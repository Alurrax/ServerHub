import os
import socket
import time

import psutil
from fastapi import APIRouter


router = APIRouter(
    prefix="/system",
    tags=["system"],
)


@router.get("/status")
def system_status():
    boot_time = psutil.boot_time()
    uptime_seconds = int(time.time() - boot_time)

    disk = psutil.disk_usage("/")

    return {
        "host": {
            "hostname": os.environ["SERVER_HOSTNAME"],
            "cpu_percent": psutil.cpu_percent(interval=0.2),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": disk.percent,
            "disk_free_gb": round(
                disk.free / (1024**3),
                2,
            ),
            "uptime_seconds": uptime_seconds,
        },
        "container": {
            "hostname": socket.gethostname(),
            "process_id": os.getpid(),
        },
    }
