from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy import asc, desc, and_

from core.model.gps_record import GpsRecord
import core.schemas.gpsrecord as gps
import core.haversine as haversine

MIN_DISTANCE = 50

async def get_gpsrecord(db: AsyncSession, record_id: int):
    result = await db.execute(
        select(GpsRecord).filter(
            GpsRecord.id == record_id
        )
    )
    return result.scalars().first()

async def get_last_gpsrecord(db: AsyncSession, device: str, app: str):
    result = await db.execute(
        select(GpsRecord).filter(
            and_(
                GpsRecord.device == device, 
                GpsRecord.app == app
            )
        ).order_by(GpsRecord.datetime.desc()).limit(1)
    )
    return result.scalars().first()

async def get_gpsrecords_by_app(db: AsyncSession, device: str, app: str, limit: int = 600):
    result = await db.execute(
        select(GpsRecord).filter(
            and_(
                GpsRecord.device == device, 
                GpsRecord.app == app
            )
        ).order_by(GpsRecord.datetime.desc()).limit(limit)
    )
    return result.scalars().all()

async def get_gpsrecords_by_device(db: AsyncSession, device: str, limit: int = 100):
    result = await db.execute(
        select(GpsRecord).filter(
            GpsRecord.device == device 
        ).order_by(GpsRecord.datetime.desc()).limit(limit).all()
    )
    return result.scalars().all()

async def get_gpsrecords(db: AsyncSession, limit: int = 100):
    result = await db.execute(
        select(GpsRecord).order_by(
            GpsRecord.datetime.desc()
        ).limit(limit)
    )
    return result.scalars().all()

async def create_gpsrecord(db: AsyncSession, gpsrecord: gps.GpsRecordCreate):
    db_gpsrecord = GpsRecord(**gpsrecord.dict())
    last = await get_last_gpsrecord(db, db_gpsrecord.device, db_gpsrecord.app)
    distance = hv_distance(db_gpsrecord,last)
    db_gpsrecord.distance = distance
    if distance >= MIN_DISTANCE:
        try:
            db.add(db_gpsrecord)
            await db.commit()
            await db.refresh(db_gpsrecord)
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
