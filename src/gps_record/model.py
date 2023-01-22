from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Float, UniqueConstraint, Index
from sqlalchemy.orm import relationship

from src.models import Base

class GpsRecord(Base):

    __tablename__ = "gps_record"

    id = Column(Integer, primary_key=True, index=True)
    datetime = Column(DateTime(timezone=True))
    latitude = Column(Float())
    longitude = Column(Float())
    altitude = Column(Float(), nullable=True)
    accuracy = Column(Float(), nullable=True)
    vertical_accuracy = Column(Float(), nullable=True)
    description = Column(String, nullable=True)
    device = Column(String(length=128))
    app = Column(String(length=128))
    user = Column(String(length=32), default='castel')
    distance = Column(Float())


Index('device_records', GpsRecord.datetime, GpsRecord.device, GpsRecord.app, GpsRecord.user, unique=True)
Index('desc_date_per_app', GpsRecord.datetime.desc(), GpsRecord.device, GpsRecord.app)
Index('per_app', GpsRecord.device, GpsRecord.app)
Index('desc_date_per_device', GpsRecord.datetime.desc(), GpsRecord.device)
Index('desc_date', GpsRecord.datetime.desc())