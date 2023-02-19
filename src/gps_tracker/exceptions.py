from fastapi import status

from src.exceptions import WhereaboutsException

class GpsTrackerException(WhereaboutsException):
    '''GpsTracker Base Exception'''
    def __init__(self, message='Generic GpsTracker Error'):
        super(GpsTrackerException, self).__init__(message)
        self.message = message
        self.type = 'GpsTracker'
        self.status  = status.HTTP_409_CONFLICT


class GpsTrackerNotFound(GpsTrackerException):
    '''The tracker does not exist'''
    def __init__(self):
        m = f'Associated GPS Tracker not found'
        super(GpsTrackerNotFound, self).__init__(m)
        self.status = status.HTTP_422_UNPROCESSABLE_ENTITY