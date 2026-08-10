import json
import socket
import subprocess

from fastapi import FastAPI


app = FastAPI(
    title="ServerHub Host Agent",
    version="0.1.0",
)


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


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "hostname": socket.gethostname(),
    }


@app.get("/disks")
def disks():
    return get_disks()
