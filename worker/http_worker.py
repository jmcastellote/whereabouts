from datetime import datetime
import os, requests, json
import core.schemas as s

token = os.environ.get('HA_TOKEN')

devices = [
    {
        'device': 'c-phone-a',
        'app': 'home-assist',
        'id': 'device_tracker.c_phone_a',
    },
    #{
    #    'device': 'c-phone-a',
    #    'app': 'own-tracks',
    #    'id': 'device_tracker.castel_cphone',
    #}
]
headers = {
        'Authorization': f'Bearer {token}',
        'content-type': 'application/json'
    }


base_url = f'http://172.18.0.1:8123/api/states/'
wa_url = f'http://172.18.0.1:8787/record/'

for device in devices:
    id = device['id']
    url = f'{base_url}{id}'
    response = requests.get(url,headers=headers)
    if response.status_code == 200:
        data = response.json()
        record = {
            'datetime': data['last_changed'],
            'latitude': data['attributes']['latitude'],
            'longitude': data['attributes']['longitude'],
            'accuracy': data['attributes']['gps_accuracy'],
            'device': device['device'],
            'app': device['app'],
            'user': 'castel'
        }
        r = requests.post(wa_url,headers=headers,json=record)