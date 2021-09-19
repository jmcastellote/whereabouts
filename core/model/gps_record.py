from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Float, UniqueConstraint, Index
from sqlalchemy.orm import relationship

from core.database import Base

class GpsRecord(Base):

    __tablename__ = "gps_record"

    id = Column(Integer, primary_key=True, index=True)
    datetime = Column(DateTime(timezone=True), index=True)
    latitude = Column(Float())
    longitude = Column(Float())
    altitude = Column(Float(),nullable=True)
    accuracy = Column(Float(),nullable=True)
    vertical_accuracy = Column(Float(),nullable=True)
    description = Column(String,nullable=True)
    device = Column(String(length=128))
    app = Column(String(length=128))
    user = Column(String(length=32), default='castel')
    distance = Column(Float())

    #UniqueConstraint('datetime','device','app','user', name='unique_device_record')
    #This needs to be executed manually
    Index('device_records','datetime','device','app','user', unique=True)