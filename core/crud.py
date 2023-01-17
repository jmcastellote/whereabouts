from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy import and_

from core.model.gps_record import GpsRecord
from core.model.gps_tracker import GpsTracker
import core.schemas.gpsrecord as gps
import core.schemas.gpstracker as gps_tracker
from core import haversine

MIN_DISTANCE = 50
DEFAULT_GPS_RECORDS_LIMIT = 1000


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
    db_session: AsyncSession,
    device: str,
    app: str,
    limit: int = DEFAULT_GPS_RECORDS_LIMIT
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


async def get_gpsrecords_by_device(db_session: AsyncSession, device: str, limit: int = DEFAULT_GPS_RECORDS_LIMIT):
    result = await db_session.execute(
        select(GpsRecord).filter(
            GpsRecord.device == device
        ).order_by(GpsRecord.datetime.desc()).limit(limit)
    )
    return result.scalars().all()


async def get_gpsrecords(db_session: AsyncSession, limit: int = DEFAULT_GPS_RECORDS_LIMIT):
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

###########################
### GpsTracker crud ops ###
###########################


async def get_gpstracker(db_session: AsyncSession, device: str, app: str, user: str):
    result = (await db_session.execute(
        select(GpsTracker).filter(
            GpsTracker.device == device,
            GpsTracker.app == app,
            GpsTracker.tracker_bearer == user,
        )
    )).scalars().all()
    if len(result) > 0:
        return result[0]
    return None


async def get_gpstracker_by_url_id(db_session: AsyncSession, url_id: str):
    result = (await db_session.execute(
        select(GpsTracker).filter(
            GpsTracker.url_id == url_id,
        )
    )).scalars().all()
    if len(result) > 0:
        return result[0]
    return None


async def create_gpstracker(db_session: AsyncSession, gpstracker: gps_tracker.GpsTrackerCreate):
    db_session_gpstracker = GpsTracker(**gpstracker.dict())
    try:
        db_session.add(db_session_gpstracker)
        await db_session.commit()
        await db_session.refresh(db_session_gpstracker)
        return db_session_gpstracker
    except IntegrityError:
        print(f'GPS Tracker \'{gpstracker.device}-{gpstracker.app}-{gpstracker.tracker_bearer}\' already exists')


async def update_gpstracker(db_session: AsyncSession, gpstracker: gps_tracker.GpsTrackerUpdate):
    db_gpstracker = (await db_session.execute(
        select(GpsTracker).filter(
            and_(
                GpsTracker.device == gpstracker.device,
                GpsTracker.app == gpstracker.app,
                GpsTracker.tracker_bearer == gpstracker.tracker_bearer
            )
        )
    )).scalars().first()
    if db_gpstracker:
        db_gpstracker.name = gpstracker.name
        db_gpstracker.icon = gpstracker.icon
        db_gpstracker.icon_config = gpstracker.icon_config
        db_gpstracker.display_path = gpstracker.display_path
        db_gpstracker.description = gpstracker.description
        db_gpstracker.app_config = gpstracker.app_config
        db_gpstracker.active = gpstracker.active
        db_gpstracker.url_id = gpstracker.url_id
        db_session.add(db_gpstracker)
        await db_session.commit()
        await db_session.refresh(db_gpstracker)
        return db_gpstracker
    else:
        print (f'GPS Tracker \'{gpstracker.device}-{gpstracker.app}-{gpstracker.tracker_bearer}\' not found')


### Helpers

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
