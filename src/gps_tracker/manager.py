from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy import and_

from src.gps_tracker.model import GpsTracker
import src.gps_tracker.schema as gps_tracker


class GpsTrackerManager:
  '''
  Helper for GpsTracker CRUD operations
  '''

  def __init__(self) -> None:
      pass


  async def get_gpstracker(self, db_session: AsyncSession, device: str, app: str, user: str):
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


  async def get_gpstracker_by_url_id(self, db_session: AsyncSession, url_id: str):
      result = (await db_session.execute(
          select(GpsTracker).filter(
              GpsTracker.url_id == url_id,
          )
      )).scalars().all()
      if len(result) > 0:
          return result[0]
      return None


  async def create_gpstracker(self, db_session: AsyncSession, gpstracker: gps_tracker.GpsTrackerCreate):
      db_session_gpstracker = GpsTracker(**gpstracker.dict())
      try:
          db_session.add(db_session_gpstracker)
          await db_session.commit()
          await db_session.refresh(db_session_gpstracker)
          return db_session_gpstracker
      except IntegrityError:
          print(f'GPS Tracker \'{gpstracker.device}-{gpstracker.app}-{gpstracker.tracker_bearer}\' already exists')


  async def update_gpstracker(self, db_session: AsyncSession, gpstracker: gps_tracker.GpsTrackerUpdate):
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