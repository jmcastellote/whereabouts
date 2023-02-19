import os
from databases import Database

TESTING = os.environ.get('TEST', None)

DATABASE_URL = os.environ.get('DATABASE_URL')
DATABASE_TEST_URL = os.environ.get('DATABASE_TEST_URL')

if TESTING:
    database = Database(DATABASE_TEST_URL, force_rollback=True)
else:
    database = Database(DATABASE_URL)