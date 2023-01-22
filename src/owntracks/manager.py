import dateparser, json
from src.gps_record.manager import GpsRecordManager
from src.owntracks.schema import OwntracksRecordBase
from src.gps_tracker.schema import GpsTracker
from src.gps_record.schema import GpsRecordCreate
from src.database import async_session
from src.salty.client import salty

class OwntracksManager(GpsRecordManager):
  '''
  Helper for GpsTracker CRUD operations
  '''

  def __init__(self, encrypted_record: dict) -> None:
      super().__init__()
      self.raw_record = json.loads(salty.decrypt(encrypted_record.data))
      

  async def create_owntracks_record(self, gpstracker: GpsTracker) -> None:
      ot_record = OwntracksRecordBase(**self.raw_record)
      record = self.build_from_ot_record(ot_record, gpstracker)
      # because this query is nearly concurrent, it needs its own session
      async with async_session() as db_session:
          await super.create_gpsrecord(db_session=db_session, gpsrecord=record)


  async def build_ot_reply(self) -> dict:
      reply = [{
          '_type': 'location',
          'lat': self.raw_record['lat'],
          'lon': self.raw_record['lon'],
          'tid': 'Jorge',
          'tst': self.raw_record['tst']
      }]
      # Display messages in the app
      #reply.append({
      #    '_type': 'cmd',
      #    'action': 'waypoints',
      #    #'content': '<b style="color: green">whereabouts is synchronized</b>'
      #})
      return {
          '_type': 'encrypted',
          'data': await salty.encrypt(json.dumps(reply))
      }


  def build_from_ot_record(self, record: OwntracksRecordBase, gpstracker: GpsTracker) -> GpsRecordCreate:
      date_settings = {
          'TIMEZONE': 'UTC',
          'RETURN_AS_TIMEZONE_AWARE': True
      }
      attr_mapper = {
          'lat': 'latitude',
          'lon': 'longitude',
          'alt': 'altitude',
          'acc': 'accuracy',
          'vac': 'vertical_accuracy',
      }
      gpsrecord = {
          'datetime': dateparser.parse(str(record.tst), settings=date_settings),
          'device': gpstracker.device,
          'app': gpstracker.app,
          'user': gpstracker.tracker_bearer
      }
      for attr, value in record.dict().items():
          if attr in attr_mapper:
              gpsrecord[attr_mapper[attr]] = value

      return GpsRecordCreate(**gpsrecord)