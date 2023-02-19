from sqlalchemy import and_, select, insert

from src.database import database
from src.gps_distance import haversine

from .model import GpsRecord
from .exceptions import GpsRecordTooClose
from . import schema as gps

class GpsRecordManager:
    '''
    Helper for GpsRecord CRUD operations
    '''

    MIN_DISTANCE = 50
    DEFAULT_GPS_RECORDS_LIMIT = 1000


    def __init__(self) -> None:
        pass


    @classmethod
    async def get_last_gpsrecord(cls, device: str, app: str, user: str):
        query = select(GpsRecord).filter(
            and_(
                GpsRecord.device == device,
                GpsRecord.app == app,
                GpsRecord.user == user
            )
        ).order_by(GpsRecord.datetime.desc())
        return await database.fetch_one(query=query)


    @classmethod
    async def get_gpsrecords_by_app(cls, device: str, app: str, limit: int = DEFAULT_GPS_RECORDS_LIMIT):
        query = select(GpsRecord).filter(
            and_(
                GpsRecord.device == device,
                GpsRecord.app == app
            )
        ).order_by(GpsRecord.datetime.desc()).limit(limit)
        return await database.fetch_all(query=query)


    @classmethod
    async def get_gpsrecords_by_device(cls, device: str, limit: int = DEFAULT_GPS_RECORDS_LIMIT):
        query = select(GpsRecord).filter(
            GpsRecord.device == device
        ).order_by(GpsRecord.datetime.desc()).limit(limit)
        return await database.fetch_all(query=query)


    @classmethod
    async def get_gpsrecords(cls, limit: int = DEFAULT_GPS_RECORDS_LIMIT):
        query = select(GpsRecord).order_by(
            GpsRecord.datetime.desc()
        ).limit(limit)
        return await database.fetch_all(query=query)


    @classmethod
    async def create_gpsrecord(cls, gpsrecord: gps.GpsRecordCreate) -> GpsRecord:
        last = await cls.get_last_gpsrecord(
            gpsrecord.device,
            gpsrecord.app,
            gpsrecord.user,
        )
        distance = cls.hv_distance(gpsrecord, last)
        gpsrecord.distance = distance
        if distance >= cls.MIN_DISTANCE:
            query = insert(GpsRecord)
            record_id = await database.execute(query=query, values=gpsrecord.dict())
            return GpsRecord(id=record_id, **gpsrecord.dict())
        else:
            raise GpsRecordTooClose(gpsrecord.app, distance, gpsrecord.accuracy)


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