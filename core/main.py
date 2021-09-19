from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from core.model.gps_record import GpsRecord
import core.crud as crud, core.schemas as schemas
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


@app.get("/records/", response_model=List[schemas.GpsRecord])
@app.get("/records/{device}/", response_model=List[schemas.GpsRecord])
@app.get("/records/{device}/{app}/", response_model=List[schemas.GpsRecord])
def get_records(device: str = None, app: str = None, limit: int = 500, db: Session = Depends(get_db)):
    if not device and not app:
        records = crud.get_gpsrecords(db, limit=limit)
    if device and not app:
        records = crud.get_gpsrecords_by_device(db, device)
    if device and app:
        records = crud.get_gpsrecords_by_app(db, device, app)
    return records


@app.post("/record/", response_model=schemas.GpsRecord)
def create_gps_record(
    gpsrecord: schemas.GpsRecordCreate, db: Session = Depends(get_db)
):
    record = crud.create_gpsrecord(db=db, gpsrecord=gpsrecord)
    if not record:
        raise HTTPException(status_code=409, detail="GPS Record already exists or is too close to last one")
    return record