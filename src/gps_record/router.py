from typing import List
from fastapi import APIRouter
from fastapi import APIRouter

from src.gps_tracker.manager import GpsTrackerManager
from src.gps_record.manager import GpsRecordManager
from src.gps_record.schema import GpsRecord, GpsRecordCreate

router = APIRouter(
    prefix="/record",
    tags=["gps_record"],
)


@router.get("/", response_model=List[GpsRecord])
async def get_all_records(limit: int = 1000):
    return await GpsRecordManager.get_gpsrecords(limit=limit)


@router.get("/{device}/", response_model=List[GpsRecord])
async def get_records_by_device(device: str = None):
    return await GpsRecordManager.get_gpsrecords_by_device(device)


@router.get("/{device}/{app}/", response_model=List[GpsRecord])
async def get_records_by_device_and_app(device: str = None, app: str = None):
    return await GpsRecordManager.get_gpsrecords_by_app(device, app)


@router.post("/", response_model=GpsRecord, status_code=201)
async def create_gps_record(gpsrecord: GpsRecordCreate):
    #check if tracker exists
    await GpsTrackerManager.get_gpstracker(
        device=gpsrecord.device, app=gpsrecord.app, user=gpsrecord.user
    )
    return await GpsRecordManager.create_gpsrecord(gpsrecord=gpsrecord)