from fastapi import Depends, FastAPI
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import check_database, get_db
from app.models import Service
from app.schemas import ServiceCreate, ServiceResponse

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


@app.post("/services", response_model=ServiceResponse)
def create_service(
    service: ServiceCreate,
    db: Session = Depends(get_db),
):
    db_service = Service(
        name=service.name,
        status=service.status,
    )

    db.add(db_service)
    db.commit()
    db.refresh(db_service)

    return db_service


@app.get("/services", response_model=list[ServiceResponse])
def list_services(
    db: Session = Depends(get_db),
):
    result = db.execute(
        select(Service).order_by(Service.id)
    )

    return result.scalars().all()
