import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from gps_record.router import router as records_router
from gps_tracker.router import router as tracker_router
from owntracks.router import router as owntracks_router


app = FastAPI()


templates = Jinja2Templates(directory="templates")


app.include_router(records_router)
app.include_router(tracker_router)
app.include_router(owntracks_router)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    '''Make sure invalid requests content is logged and define error output and logging format'''
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    logging.error(f"{request}: {exc_str}")
    content = {'error': 'Validation Error', 'message': exc_str, 'data': None}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
