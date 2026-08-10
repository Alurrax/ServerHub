from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Service
from app.schemas import ServiceCreate, ServiceResponse

router = APIRouter(
    prefix="/services",
    tags=["services"],
)


@router.post("", response_model=ServiceResponse)
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


@router.get("", response_model=list[ServiceResponse])
def list_services(
    db: Session = Depends(get_db),
):
    result = db.execute(
        select(Service).order_by(Service.id)
    )

    return result.scalars().all()
