import asyncio
import os, aiohttp

token = os.environ.get('HA_TOKEN')

devices = [
    {
        'device': 'c-phone-9',
        'app': 'home-assistant',
        'id': 'device_tracker.c_phone_9',
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

async def fetch_gps_records_from_ha() -> None:
    for device in devices:
        id = device['id']
        url = f'{base_url}{id}'
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as resp:
                status = resp.status
                response = await resp.json()
        if status == 200:
            data = response
            record = {
                'datetime': data['last_changed'],
                'latitude': data['attributes']['latitude'],
                'longitude': data['attributes']['longitude'],
                'accuracy': data['attributes']['gps_accuracy'],
                'device': device['device'],
                'app': device['app'],
                'user': 'castel'
            }
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.post(wa_url, json=record) as resp:
                    status = resp.status
            print(f'record from {record["app"]} sent, status {status}')

asyncio.run(fetch_gps_records_from_ha())