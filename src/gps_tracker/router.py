from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter
from fastapi import Depends, APIRouter, HTTPException

from src.database import get_session
from src.gps_tracker.manager import GpsTrackerManager
from src.gps_tracker.schema import GpsTracker, GpsTrackerCreate, GpsTrackerUpdate


router = APIRouter(
    prefix="/tracker",
    tags=["tracker"],
)


@router.post("/", response_model=GpsTracker, status_code=201)
async def create_tracker(gpstracker: GpsTrackerCreate, db_session: AsyncSession = Depends(get_session)
):
    record = await GpsTrackerManager().create_gpstracker(db_session=db_session, gpstracker=gpstracker)
    if not record:
        raise HTTPException(status_code=409, detail="Tracker already exists")
    return record


@router.put("/", response_model=GpsTracker)
async def update_tracker(gpstracker: GpsTrackerUpdate, db_session: AsyncSession = Depends(get_session)
):
    record = await GpsTrackerManager().update_gpstracker(db_session=db_session, gpstracker=gpstracker)
    if not record:
        raise HTTPException(status_code=422, detail="Tracker not found")
    return record
