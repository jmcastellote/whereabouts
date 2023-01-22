from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float, Index, JSON

from src.models import Base

class GpsTracker(Base):

    __tablename__ = "gps_tracker"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(length=128))
    device = Column(String(length=128))
    app = Column(String(length=128))
    last_seen = Column(DateTime(timezone=True),nullable=True)
    icon = Column(String(length=512))
    icon_config = Column(JSON())
    display_path = Column(Boolean())
    description = Column(String,nullable=True)
    tracker_bearer = Column(String(length=128), default='castel', index=True)
    distance_tracked = Column(Float())
    url_id = Column(String(length=16), index=True, unique=True)
    app_config = Column(JSON())
    active = Column(Boolean(), default=True)

Index('unique_tracker', GpsTracker.device, GpsTracker.app, GpsTracker.tracker_bearer, unique=True)