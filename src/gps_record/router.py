from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter
from fastapi import Depends, APIRouter, HTTPException

from src.gps_tracker.manager import GpsTrackerManager
from src.database import get_session
from src.gps_record.manager import GpsRecordManager
from src.gps_record.schema import GpsRecord, GpsRecordCreate

router = APIRouter(
    prefix="/records",
    tags=["records"],
)



@router.get("/", response_model=List[GpsRecord])
async def get_all_records(limit: int = 1000, db_session: AsyncSession = Depends(get_session)):
    return await GpsRecordManager.get_gpsrecords(db_session, limit=limit)


@router.get("/{device}/", response_model=List[GpsRecord])
async def get_records_by_device(
    device: str = None, db_session: AsyncSession = Depends(get_session)
):
    return await GpsRecordManager.get_gpsrecords_by_device(db_session, device)


@router.get("/{device}/{app}/", response_model=List[GpsRecord])
async def get_records_by_device_and_app(
    device: str = None, 
    app: str = None,
    db_session: AsyncSession = Depends(get_session)
):
    return await GpsRecordManager.get_gpsrecords_by_app(db_session, device, app)


@router.post("/", response_model=GpsRecord, status_code=201)
async def create_gps_record(gpsrecord: GpsRecordCreate, db_session: AsyncSession = Depends(get_session)):
    #check if tracker exists
    gps_tracker = await GpsTrackerManager().get_gpstracker(
        db_session=db_session, device=gpsrecord.device, app=gpsrecord.app, user=gpsrecord.user
    )
    if gps_tracker:
        record = await GpsRecordManager.create_gpsrecord(db_session=db_session, gpsrecord=gpsrecord)
        if not record:
            raise HTTPException(status_code=409, detail="GPS Record already exists or is too close to last one")
        return record
    raise HTTPException(status_code=422, detail="Associated GPS Tracker not found")