import os, json, dateparser
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from nacl.encoding import Base64Encoder
from pydantic import ValidationError
import nacl.secret as salt

from core.model.gps_record import GpsRecord
import core.crud as crud
import core.schemas.gpsrecord as gps
import core.schemas.owntracks as ot
from core.database import SessionLocal, engine

#needed only once
#models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://cadmin",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/records/", response_model=List[gps.GpsRecord])
@app.get("/records/{device}/", response_model=List[gps.GpsRecord])
@app.get("/records/{device}/{app}/", response_model=List[gps.GpsRecord])
def get_records(device: str = None, app: str = None, limit: int = 500, db: Session = Depends(get_db)):
    if not device and not app:
        records = crud.get_gpsrecords(db, limit=limit)
    if device and not app:
        records = crud.get_gpsrecords_by_device(db, device)
    if device and app:
        records = crud.get_gpsrecords_by_app(db, device, app)
    return records


@app.post("/record/", response_model=gps.GpsRecord)
def create_gps_record(
    gpsrecord: gps.GpsRecordCreate, db: Session = Depends(get_db)
):
    record = crud.create_gpsrecord(db=db, gpsrecord=gpsrecord)
    if not record:
        raise HTTPException(status_code=409, detail="GPS Record already exists or is too close to last one")
    return record


seed = os.environ.get('OT_SEED')
box = salt.SecretBox(bytes(seed,'utf-8'))
@app.post('/owntracks/{ot_url_path}', status_code=200)
async def owntracks_record(encrypted_record: ot.OwntracksEncryptedRecordBase):
    dp_settings = {'TIMEZONE': 'UTC', 'RETURN_AS_TIMEZONE_AWARE': True}
    raw_record = box.decrypt(encrypted_record.data, encoder=Base64Encoder)
    try:
        record = ot.OwntracksRecordBase(**json.loads(raw_record.decode('utf-8')))
        print (record)
        print (f'timestamp: {dateparser.parse(str(record.tst), settings=dp_settings)}')
    except ValidationError:
        print ('This one didnt like it')
        print (raw_record)
    return {}
    
   # return {
   #     '_type': 'cmd',
   #     'action': 'reportLocation'
   # }
