import os, json, dateparser
import asyncio
from asyncio import Task
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from core.classes.salty import Salty
from core.model.gps_record import GpsRecord
import core.crud as crud
import core.schemas.gpsrecord as gps
import core.schemas.owntracks as ot
from core.database import get_session

#needed only once
#models.Base.metadata.create_all(bind=engine)

app = FastAPI()

templates = Jinja2Templates(directory="templates")

salty = Salty(os.environ.get('OT_SEED'))

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/records/", response_model=List[gps.GpsRecord])
async def get_all_records(limit: int = 500, db: AsyncSession = Depends(get_session)):
        return await crud.get_gpsrecords(db, limit=limit)

@app.get("/records/{device}/", response_model=List[gps.GpsRecord])
async def get_records_by_device(device: str = None, db: AsyncSession = Depends(get_session)):
        return await crud.get_gpsrecords_by_device(db, device)

@app.get("/records/{device}/{app}/", response_model=List[gps.GpsRecord])
async def get_records(device: str = None, app: str = None, db: AsyncSession = Depends(get_session)):
        return await crud.get_gpsrecords_by_app(db, device, app)

@app.post("/record/", response_model=gps.GpsRecord)
async def create_gps_record(
    gpsrecord: gps.GpsRecordCreate, db: AsyncSession = Depends(get_session)
):
    record = await crud.create_gpsrecord(db=db, gpsrecord=gpsrecord)
    if not record:
        raise HTTPException(status_code=409, detail="GPS Record already exists or is too close to last one")
    return record

@app.post('/owntracks/{ot_url_path}', status_code=200)
async def owntracks_record(encrypted_record: ot.OwntracksEncryptedRecordBase):
    asyncio.create_task(
        task_waiter(process_owntracks_record(encrypted_record.data))
    )
    return {}

async def process_owntracks_record(encrypted_bytes: bytes):
    dp_settings = {
        'TIMEZONE': 'UTC', 
        'RETURN_AS_TIMEZONE_AWARE': True
    }
    raw_record = await salty.decrypt(encrypted_bytes)
    try:
        record = ot.OwntracksRecordBase(
            **json.loads(raw_record.decode('utf-8'))
        )
        print (record)
        print (f'timestamp: {dateparser.parse(str(record.tst), settings=dp_settings)}')
    except ValidationError:
        print ('This one didnt like it')
        print (raw_record)

async def task_waiter(task: Task):
    await asyncio.sleep(3)
    await task
    print('done')