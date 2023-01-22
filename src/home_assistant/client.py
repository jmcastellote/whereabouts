import os
import aiohttp

class HomeAssistant:

    def __init__(self) -> None:
        pass


    @classmethod
    async def forward (cls, data: bytes) -> int:
        url = os.environ.get('HA_FORWARDING_URL')
        body = {
            '_type': 'encrypted',
            'data': data.decode('utf-8')
        }
        headers = {
            'X-Limit-U': 'castel',
            'X-Limit-D': 'cphone',
        }
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(url, json=body) as resp:
                print (f'message forwarded to home assistant, result {resp.status}')
