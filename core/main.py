import asyncio
from typing import List
import os
import json
import dateparser
import aiohttp

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from core.classes.salty import Salty
from core import crud
import core.schemas.gpsrecord as gps
import core.schemas.owntracks as ot
from core.database import get_session


app = FastAPI()

templates = Jinja2Templates(directory="templates")

salty = Salty(os.environ.get('OT_SEED'))

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/records/", response_model=List[gps.GpsRecord])
async def get_all_records(limit: int = 1000, db_session: AsyncSession = Depends(get_session)):
    return await crud.get_gpsrecords(db_session, limit=limit)

@app.get("/records/{device}/", response_model=List[gps.GpsRecord])
async def get_records_by_device(
    device: str = None, db_session: AsyncSession = Depends(get_session)
):
    return await crud.get_gpsrecords_by_device(db_session, device)

@app.get("/records/{device}/{tracker_app}/", response_model=List[gps.GpsRecord])
async def get_records(
    device: str = None, 
    tracker_app: str = None,
    db_session: AsyncSession = Depends(get_session)
):
    return await crud.get_gpsrecords_by_app(db_session, device, tracker_app)

@app.post("/record/", response_model=gps.GpsRecord)
async def create_gps_record(
    gpsrecord: gps.GpsRecordCreate, db_session: AsyncSession = Depends(get_session)
):
    record = await crud.create_gpsrecord(db_session=db_session, gpsrecord=gpsrecord)
    if not record:
        raise HTTPException(
            status_code=409,
            detail="GPS Record already exists or is too close to last one"
        )
    return record

@app.post('/owntracks/309b5ffc2df9', status_code=200)
async def owntracks_record(
    encrypted_record: ot.OwntracksEncryptedRecordBase,
    db_session: AsyncSession = Depends(get_session)
):
    raw_record = json.loads(await salty.decrypt(encrypted_record.data))
    print(raw_record)
    asyncio.create_task(save_owntracks_record(raw_record, db_session))
    if raw_record['_type'] == 'location' or raw_record['_type'] == 'transition':
        #asyncio.create_task(forward_to_ha(encrypted_record.data))
        return await build_ot_reply(raw_record)
    return []

async def build_ot_reply(raw_record: dict) -> dict:
    reply = [{
        '_type': 'location',
        'lat': raw_record['lat'],
        'lon': raw_record['lon'],
        'tid': 'J',
        'tst': raw_record['tst']
    }]
    #reply.append({
    #    '_type': 'cmd',
    #    'action': 'waypoints',
    #    #'content': '<b style="color: green">whereabouts is synchronized</b>'
    #})
    print(reply)
    return {
        '_type': 'encrypted',
        'data': await salty.encrypt(json.dumps(reply))
    }

async def save_owntracks_record(raw_record: dict, db_session: AsyncSession = Depends(get_session)):
    try:
        ot_record = ot.OwntracksRecordBase(**raw_record)
        record = build_from_ot_record(ot_record)
        await crud.create_gpsrecord(db_session=db_session, gpsrecord=record)
        # This is needed when the session goes out of scope
        # (in this case is non awaited task)
        # see tip under https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html#synopsis-core
        await db_session.close()
    except ValidationError:
        print ('This one didnt like it')
        print (raw_record)

def build_from_ot_record(record: ot.OwntracksRecordBase) -> gps.GpsRecordCreate:
    date_settings = {
        'TIMEZONE': 'UTC',
        'RETURN_AS_TIMEZONE_AWARE': True
    }
    attr_mapper = {
        'lat': 'latitude',
        'lon': 'longitude',
        'alt': 'altitude',
        'acc': 'accuracy',
        'vac': 'vertical_accuracy',
    }
    gpsrecord = {
        'datetime': dateparser.parse(str(record.tst), settings=date_settings),
        'device': 'c-phone-a',
        'app': 'own-tracks',
        'user': 'castel'
    }
    for attr, value in record.dict().items():
        if attr in attr_mapper:
            gpsrecord[attr_mapper[attr]] = value

    return gps.GpsRecordCreate(**gpsrecord)

async def forward_to_ha(data: bytes):
    url = 'http://172.18.0.1:8123/api/webhook/d6d5f6436567de9cab9273d4ce53329e49f8d1230cda82ccadb7e8dc6fd7f4af'
    body = {
        '_type': 'encrypted',
        'data': data.decode('utf-8')
    }
    headers = {
        'X-Limit-U': 'castel',
        'X-Limit-D': 'cphone',
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(url, json=body) as resp:
            #r = await resp.json()
            print (f'message forwarded to home assistant, result {resp.status}')
