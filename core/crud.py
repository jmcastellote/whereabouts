from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import asc, desc, and_

from core.model.gps_record import GpsRecord
import core.schemas as schemas
import core.haversine as haversine

MIN_DISTANCE = 50

def get_gpsrecord(db: Session, record_id: int):
    return db.query(GpsRecord).filter(GpsRecord.id == record_id).first()

def get_last_gpsrecord(db: Session, device: str, app: str):
    return db.query(GpsRecord).filter(
        and_(
            GpsRecord.device == device, 
            GpsRecord.app == app
        )
    ).order_by(GpsRecord.datetime.desc()).first()

def get_gpsrecords_by_app(db: Session, device: str, app: str, limit: int = 100):
    return db.query(GpsRecord).filter(
        and_(
            GpsRecord.device == device, 
            GpsRecord.app == app
        )
    ).order_by(GpsRecord.datetime.desc()).limit(limit).all()

def get_gpsrecords_by_device(db: Session, device: str, limit: int = 100):
    return db.query(GpsRecord).filter(
            GpsRecord.device == device 
    ).order_by(GpsRecord.datetime.desc()).limit(limit).all()

def get_gpsrecords(db: Session, limit: int = 100):
    return db.query(GpsRecord).order_by(GpsRecord.datetime.desc()).limit(limit).all()

def create_gpsrecord(db: Session, gpsrecord: schemas.GpsRecordCreate):
    db_gpsrecord = GpsRecord(**gpsrecord.dict())
    last = get_last_gpsrecord(db, db_gpsrecord.device, db_gpsrecord.app)
    distance = hv_distance(db_gpsrecord,last)
    if distance >= MIN_DISTANCE:
        try:
            db.add(db_gpsrecord)
            db.commit()
            db.refresh(db_gpsrecord)
            return db_gpsrecord
        except IntegrityError:
            print(f'record received for {gpsrecord.app} on {gpsrecord.datetime} but already existed')
    else:
        print(f'skipping record for {gpsrecord.app}, is too close from last one ({distance}m, acc: {gpsrecord.accuracy})')

def hv_distance(gps_record_1: GpsRecord, gps_record_2: GpsRecord) -> float:
    if not gps_record_1 or not gps_record_2:
        return MIN_DISTANCE
    distance = haversine.haversine(
        gps_record_1.longitude,
        gps_record_1.latitude,
        gps_record_2.longitude,
        gps_record_2.latitude
    )
    return distance