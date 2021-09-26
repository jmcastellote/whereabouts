from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Float, UniqueConstraint, Index, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import null

from core.database import Base

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
    tracker_bearer = Column(String(length=128), default='castel')
    distance_tracked = Column(Float())

    #UniqueConstraint('datetime','device','app','user', name='unique_device_record')
    #This needs to be executed manually
    Index('device_records','datetime','device','app','user', unique=True)