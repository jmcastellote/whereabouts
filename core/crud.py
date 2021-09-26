from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy import and_

from core.model.gps_record import GpsRecord
import core.schemas.gpsrecord as gps
from core import haversine

MIN_DISTANCE = 50


async def get_gpsrecord(db_session: AsyncSession, record_id: int):
    result = await db_session.execute(
        select(GpsRecord).filter(
            GpsRecord.id == record_id
        )
    )
    return result.scalars().first()


async def get_last_gpsrecord(db_session: AsyncSession, device: str, app: str):
    result = await db_session.execute(
        select(GpsRecord).filter(
            and_(
                GpsRecord.device == device,
                GpsRecord.app == app
            )
        ).order_by(GpsRecord.datetime.desc()).limit(1)
    )
    return result.scalars().first()


async def get_gpsrecords_by_app(
    db_session: AsyncSession, device: str,
    app: str,
    limit: int = 600
):
    result = await db_session.execute(
        select(GpsRecord).filter(
            and_(
                GpsRecord.device == device,
                GpsRecord.app == app
            )
        ).order_by(GpsRecord.datetime.desc()).limit(limit)
    )
    return result.scalars().all()


async def get_gpsrecords_by_device(db_session: AsyncSession, device: str, limit: int = 100):
    result = await db_session.execute(
        select(GpsRecord).filter(
            GpsRecord.device == device
        ).order_by(GpsRecord.datetime.desc()).limit(limit).all()
    )
    return result.scalars().all()


async def get_gpsrecords(db_session: AsyncSession, limit: int = 100):
    result = await db_session.execute(
        select(GpsRecord).order_by(
            GpsRecord.datetime.desc()
        ).limit(limit)
    )
    return result.scalars().all()


async def create_gpsrecord(db_session: AsyncSession, gpsrecord: gps.GpsRecordCreate):
    db_session_gpsrecord = GpsRecord(**gpsrecord.dict())
    last = await get_last_gpsrecord(
        db_session,
        db_session_gpsrecord.device,
        db_session_gpsrecord.app
    )
    distance = hv_distance(db_session_gpsrecord, last)
    db_session_gpsrecord.distance = distance
    if distance >= MIN_DISTANCE:
        try:
            db_session.add(db_session_gpsrecord)
            await db_session.commit()
            await db_session.refresh(db_session_gpsrecord)
            return db_session_gpsrecord
        except IntegrityError:
            print(
                f'record received for {gpsrecord.app} on {gpsrecord.datetime} but already existed'
            )
    else:
        print(
            f' skipping record for {gpsrecord.app}, is too close from last one ({distance:.2f}m, acc: {gpsrecord.accuracy})'
        )


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
