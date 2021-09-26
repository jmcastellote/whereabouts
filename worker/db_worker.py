from datetime import datetime
import os, requests, json
import core.crud, core.schemas as s
from core.database import SessionLocal, engine
from sqlalchemy.exc import IntegrityError

token = os.environ.get('HA_TOKEN')

devices = [
    {
        'device': 'c-phone-a',
        'app': 'home-assist',
        'id': 'device_tracker.c_phone_a',
    },
    {
        'device': 'c-phone-a',
        'app': 'own-tracks',
        'id': 'device_tracker.castel_cphone',
    }
]
headers = {
        'Authorization': f'Bearer {token}',
        'content-type': 'application/json'
    }


base_url = f'http://172.18.0.1:8123/api/states/'

db = SessionLocal()
for device in devices:
    id = device['id']
    url = f'{base_url}{id}'
    response = requests.get(url,headers=headers)
    if response.status_code == 200:
        data = response.json()
        record = s.GpsRecordCreate(
            datetime=data['last_changed'],
            latitude=data['attributes']['latitude'],
            longitude=data['attributes']['longitude'],
            accuracy=data['attributes']['gps_accuracy'],
            device=device['device'],
            app=device['app'],
            user='castel'
        )
        try:
            r = core.crud.create_gpsrecord(db,record)
            print(f'record from {record.app} added')
        except IntegrityError:
            print(f'record from {record.app} at {record.datetime} already existed')
db.close()