from pydantic import BaseModel, constr, validator
from datetime import datetime

class GpsTrackerBase(BaseModel):

    name: constr(max_length=128)
    device: constr(max_length=128)
    app: constr(max_length=128)
    last_seen: datetime = None
    icon: constr(max_length=512)
    icon_config: dict = {}
    display_path: bool
    description: str = None
    tracker_bearer: constr(max_length=128)
    distance_tracked: float = 0
    url_id: constr(max_length=16)
    app_config: dict = {}
    active: bool = True


class GpsTrackerCreate(GpsTrackerBase):
    pass

class GpsTrackerUpdate(GpsTrackerBase):
    pass

class GpsTracker(GpsTrackerBase):
    id: int

    class Config:
        orm_mode = True