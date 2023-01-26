from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel


class GpsRecordBase(BaseModel):
    datetime: datetime
    description: Optional[str]
    latitude: float
    longitude: float
    altitude: Optional[float]
    accuracy: Optional[float]
    vertical_accuracy: Optional[float]
    device: str
    app: str
    user: str
    distance: Optional[float]


class GpsRecordCreate(GpsRecordBase):
    pass


class GpsRecord(GpsRecordBase):
    id: int

    class Config:
        orm_mode = True