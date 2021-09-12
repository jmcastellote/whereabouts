from sqlalchemy.orm import Session

import models, schemas


def get_gpsrecord(db: Session, record_id: int):
    return db.query(models.GpsRecord).filter(models.GpsRecord.id == record_id).first()


def get_gpsrecords_by_app(db: Session, device: str, app: str):
    return db.query(models.GpsRecord).filter(
        and_(
            models.GpsRecord.device == device, 
            models.GpsRecord.app == app
        )
    )

def get_gpsrecords(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.GpsRecord).offset(skip).limit(limit).all()

def create_gpsrecord(db: Session, gpsrecord: schemas.GpsRecordCreate):
    db_gpsrecord = models.Item(**gpsrecord.dict())
    db.add(db_gpsrecord)
    db.commit()
    db.refresh(db_gpsrecord)
    return db_gpsrecord