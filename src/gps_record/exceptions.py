from src.exceptions import WhereaboutsException


class GpsRecordException(WhereaboutsException):
    '''GpsRecord Base Exception'''
    def __init__(self, message='Generic GpsRecord Error'):
        super(GpsRecordException, self).__init__(message)
        self.message = message
        self.type = 'GpsRecord'
        self.status = 409


class GpsRecordTooClose(GpsRecordException):
    '''Received GPS record is too close from the last one'''
    def __init__(self, app, distance, accuracy):
        m = f' skipping record for {app}, is too close from last one ({distance:.2f}m, acc: {accuracy})'
        super(GpsRecordTooClose, self).__init__(m)
        self.message = m