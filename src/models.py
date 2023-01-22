from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

import src.gps_record.model
import src.gps_tracker.model