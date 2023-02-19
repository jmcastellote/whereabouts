import logging
from fastapi import status, Request
from fastapi.exceptions import RequestValidationError
from asyncpg.exceptions import UniqueViolationError
from fastapi.responses import JSONResponse

class WhereaboutsException(Exception):
    def __init__(self, message='generic whereabouts error!'):
        super(WhereaboutsException, self).__init__(message)
        self.message = message
        self.type = 'Whereabouts'
        self.status  = status.HTTP_409_CONFLICT

class WhereaboutsExceptionHandler:

    @classmethod
    async def validation_exception_handler(cls, request: Request, exc: RequestValidationError):
        '''Make sure invalid requests content is logged and define error output and logging format'''
        exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
        logging.error(f"{request}: {exc_str}")
        content = {'error': 'Validation Error', 'message': exc_str}
        return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    @classmethod
    async def duplicates_exception_handler(cls, request: Request, exc: UniqueViolationError):
        '''Duplicated Objects'''
        logging.error(f"{request.url.path}: {exc.detail}")
        content = {'error': 'Object already exists', 'message': exc.detail}
        return JSONResponse(content=content, status_code=status.HTTP_409_CONFLICT)

    @classmethod
    async def handle(cls, request: Request, exc: WhereaboutsException):
        '''Whereabouts Errors'''
        logging.error(f"{request.url.path}: {exc.message}")
        content = {'error': f'{exc.type} Error', 'message': exc.message}
        return JSONResponse(content=content, status_code=exc.status)