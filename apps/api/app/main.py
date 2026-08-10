from fastapi import FastAPI

from app.database import check_database

app = FastAPI(
    title="ServerHub API",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "name": "ServerHub",
        "status": "running",
    }


@app.get("/health")
def health():
    check_database()

    return {
        "status": "healthy",
        "database": "connected",
    }
