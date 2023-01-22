from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy import and_

from src.gps_record.model import GpsRecord
import src.gps_record.schema as gps
from src.gps_distance import haversine

class GpsRecordManager:
    '''
    Helper for GpsRecord CRUD operations
    '''

    MIN_DISTANCE = 50
    DEFAULT_GPS_RECORDS_LIMIT = 1000


    def __init__(self) -> None:
        pass

    @classmethod
    async def get_gpsrecord(cls, db_session: AsyncSession, record_id: int):
        result = await db_session.execute(
            select(GpsRecord).filter(
                GpsRecord.id == record_id
            )
        )
        return result.scalars().first()


    @classmethod
    async def get_last_gpsrecord(cls, db_session: AsyncSession, device: str, app: str, user: str):
        result = await db_session.execute(
            select(GpsRecord).filter(
                and_(
                    GpsRecord.device == device,
                    GpsRecord.app == app,
                    GpsRecord.user == user
                )
            ).order_by(GpsRecord.datetime.desc()).limit(1)
        )
        return result.scalars().first()


    @classmethod
    async def get_gpsrecords_by_app(
        cls,
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


    @classmethod
    async def get_gpsrecords_by_device(cls, db_session: AsyncSession, device: str, limit: int = DEFAULT_GPS_RECORDS_LIMIT):
        result = await db_session.execute(
            select(GpsRecord).filter(
                GpsRecord.device == device
            ).order_by(GpsRecord.datetime.desc()).limit(limit)
        )
        return result.scalars().all()


    @classmethod
    async def get_gpsrecords(cls, db_session: AsyncSession, limit: int = DEFAULT_GPS_RECORDS_LIMIT):
        result = await db_session.execute(
            select(GpsRecord).order_by(
                GpsRecord.datetime.desc()
            ).limit(limit)
        )
        return result.scalars().all()


    @classmethod
    async def create_gpsrecord(cls, db_session: AsyncSession, gpsrecord: gps.GpsRecordCreate):
        db_session_gpsrecord = GpsRecord(**gpsrecord.dict())
        last = await cls.get_last_gpsrecord(
            db_session,
            db_session_gpsrecord.device,
            db_session_gpsrecord.app,
            db_session_gpsrecord.user,
        )
        distance = cls.hv_distance(db_session_gpsrecord, last)
        db_session_gpsrecord.distance = distance
        if distance >= cls.MIN_DISTANCE:
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


    @classmethod
    def hv_distance(self, gps_record_1: GpsRecord, gps_record_2: GpsRecord) -> float:
        if not gps_record_1 or not gps_record_2:
            return self.MIN_DISTANCE
        distance = haversine.haversine(
            gps_record_1.longitude,
            gps_record_1.latitude,
            gps_record_2.longitude,
            gps_record_2.latitude
        )
        return distance