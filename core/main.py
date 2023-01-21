import asyncio
from typing import List
import os
import json
import aiohttp
import logging

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from core.classes.gps_record_manager import GpsRecordManager
from core.classes.gps_tracker_manager import GpsTrackerManager
from core.classes.owntracks_manager import OwntracksManager
from core.classes.home_assistant import HomeAssistant
import core.schemas.gpsrecord as gps
import core.schemas.gpstracker as gpstracker
import core.schemas.owntracks as ot
from core.database import get_session


app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/records/", response_model=List[gps.GpsRecord])
async def get_all_records(limit: int = 1000, db_session: AsyncSession = Depends(get_session)):
    return await GpsRecordManager().get_gpsrecords(db_session, limit=limit)


@app.get("/records/{device}/", response_model=List[gps.GpsRecord])
async def get_records_by_device(
    device: str = None, db_session: AsyncSession = Depends(get_session)
):
    return await GpsRecordManager().get_gpsrecords_by_device(db_session, device)


@app.get("/records/{device}/{tracker_app}/", response_model=List[gps.GpsRecord])
async def get_records(
    device: str = None, 
    tracker_app: str = None,
    db_session: AsyncSession = Depends(get_session)
):
    return await GpsRecordManager().get_gpsrecords_by_app(db_session, device, tracker_app)


@app.post("/record/", response_model=gps.GpsRecord, status_code=201)
async def create_gps_record(gpsrecord: gps.GpsRecordCreate, db_session: AsyncSession = Depends(get_session)):
    #check if tracker exists
    gps_tracker = await GpsTrackerManager().get_gpstracker(
        db_session=db_session, device=gpsrecord.device, app=gpsrecord.app, user=gpsrecord.user
    )
    if gps_tracker:
        record = await GpsRecordManager().create_gpsrecord(db_session=db_session, gpsrecord=gpsrecord)
        if not record:
            raise HTTPException(status_code=409, detail="GPS Record already exists or is too close to last one")
        return record
    raise HTTPException(status_code=422, detail="Associated GPS Tracker not found")


@app.post("/tracker/", response_model=gpstracker.GpsTracker, status_code=201)
async def create_tracker(
    gpstracker: gpstracker.GpsTrackerCreate,
    db_session: AsyncSession = Depends(get_session)
):
    record = await GpsTrackerManager().create_gpstracker(db_session=db_session, gpstracker=gpstracker)
    if not record:
        raise HTTPException(status_code=409, detail="Tracker already exists")
    return record


@app.put("/tracker/", response_model=gpstracker.GpsTracker)
async def update_tracker(
    gpstracker: gpstracker.GpsTrackerUpdate,
    db_session: AsyncSession = Depends(get_session)
):
    record = await GpsTrackerManager().update_gpstracker(db_session=db_session, gpstracker=gpstracker)
    if not record:
        raise HTTPException(
            status_code=422,
            detail="Tracker not found"
        )
    return record


@app.post('/owntracks/{url_id}/', response_model=dict, status_code=200)
async def owntracks_record(
    encrypted_record: ot.OwntracksEncryptedRecordBase,
    db_session: AsyncSession = Depends(get_session),
    url_id: str = None
):
    # check if it's a known owntracks tracker (by checking the url_id)
    gps_tracker = await GpsTrackerManager().get_gpstracker_by_url_id(db_session=db_session,url_id=url_id)
    if gps_tracker:
        otm = OwntracksManager(encrypted_record=encrypted_record)
        asyncio.create_task(otm.create_owntracks_record(gpstracker=gps_tracker))
        if otm.raw_record['_type'] in ['location', 'transition']:
            if os.environ.get('FORWARD_TO_HA') in ['true','True','yes','Yes']:
                asyncio.create_task(HomeAssistant.forward(encrypted_record.data))
            return await otm.build_ot_reply()
        return []
    raise HTTPException(status_code=422, detail="Tracker not found")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    '''Make sure invalid requests content is logged and define error output and logging format'''
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    logging.error(f"{request}: {exc_str}")
    content = {'error': 'Validation Error', 'message': exc_str, 'data': None}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)