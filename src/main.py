import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from asyncpg.exceptions import UniqueViolationError

from gps_record.router import router as records_router
from gps_tracker.router import router as tracker_router
from owntracks.router import router as owntracks_router

from .database import database
from .exceptions import WhereaboutsException, WhereaboutsExceptionHandler


app = FastAPI()


templates = Jinja2Templates(directory="../templates")


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


### Register routers ###

app.include_router(records_router)
app.include_router(tracker_router)
app.include_router(owntracks_router)


### Register exception handlers ###

# Validation Errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return await WhereaboutsExceptionHandler.validation_exception_handler(request, exc)

# Unique Key Violations (duplicated objects)
@app.exception_handler(UniqueViolationError)
async def duplicates_exception_handler(request: Request, exc: UniqueViolationError):
    return await WhereaboutsExceptionHandler.duplicates_exception_handler(request, exc)

# Whereabouts Exceptions
@app.exception_handler(WhereaboutsException)
async def duplicates_exception_handler(request: Request, exc: WhereaboutsException):
    return await WhereaboutsExceptionHandler.handle(request, exc)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})