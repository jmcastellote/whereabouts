from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

import crud, models, schemas
from database import SessionLocal, engine

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

@app.get("/records/", response_model=List[schemas.GpsRecord])
def get_records(skip: int = 0, limit: int = 500, db: Session = Depends(get_db)):
    records = crud.get_gpsrecords(db, skip=skip, limit=limit)
    return records