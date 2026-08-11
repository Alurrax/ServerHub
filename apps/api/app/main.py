from fastapi import FastAPI

from app.database import check_database
from app.routers.services import router as services_router

from app.routers.system import router as system_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="ServerHub API",
    version="0.1.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://192.168.1.9:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(services_router)
app.include_router(system_router)



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
