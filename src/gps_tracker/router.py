from fastapi import APIRouter
from fastapi import APIRouter

from src.gps_tracker.manager import GpsTrackerManager
from src.gps_tracker.schema import GpsTracker, GpsTrackerCreate, GpsTrackerUpdate


router = APIRouter(
    prefix="/tracker",
    tags=["gps_tracker"],
)


@router.post("/", response_model=GpsTracker, status_code=201)
async def create_tracker(gpstracker: GpsTrackerCreate):
    return await GpsTrackerManager.create_gpstracker(gpstracker=gpstracker)


@router.put("/", response_model=GpsTrackerUpdate)
async def update_tracker(gpstracker: GpsTrackerUpdate):
    return await GpsTrackerManager.update_gpstracker(gpstracker=gpstracker)
