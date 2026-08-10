from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ServiceCreate(BaseModel):
    name: str
    status: str = "unknown"
    description: str | None = None


class ServiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    status: str
    description: str | None
    created_at: datetime
