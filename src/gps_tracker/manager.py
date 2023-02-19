from sqlalchemy import and_, select, insert, update

from src.database import database

from .model import GpsTracker
from .exceptions import GpsTrackerNotFound
from . import schema as gps_tracker


class GpsTrackerManager:
    '''
    Helper for GpsTracker CRUD operations
    '''

    def __init__(self) -> None:
        pass


    async def get_gpstracker(self, device: str, app: str, user: str):
        query = select(GpsTracker).filter(
            GpsTracker.device == device,
            GpsTracker.app == app,
            GpsTracker.tracker_bearer == user,
        )
        result = await database.fetch_one(query=query)
        if not result:
            raise GpsTrackerNotFound()
        return result


    async def get_gpstracker_by_url_id(self, url_id: str):
        query = select(GpsTracker).filter(GpsTracker.url_id == url_id)
        return await database.fetch_one(query=query)


    async def create_gpstracker(self, gpstracker: gps_tracker.GpsTrackerCreate) -> GpsTracker:
        query = insert(GpsTracker)
        tracker_id = await database.execute(query=query, values=gpstracker.dict())
        return GpsTracker(id=tracker_id, **gpstracker.dict())


    async def update_gpstracker(self, gpstracker: gps_tracker.GpsTrackerUpdate) -> gps_tracker.GpsTracker:
        db_gpstracker = await self.get_gpstracker(gpstracker.device, gpstracker.app, gpstracker.tracker_bearer)
        query = update(GpsTracker).where(and_(
            GpsTracker.device == gpstracker.device,
            GpsTracker.app == gpstracker.app,
            GpsTracker.tracker_bearer == gpstracker.tracker_bearer
        ))
        await database.execute(query=query, values=gpstracker.dict())
        return db_gpstracker
