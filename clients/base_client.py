import aiohttp
import json
import time
import hashlib
import random
import string
from config.settings import SECRET_KEY, APP_ID, FRONT_VERSION, USER_AGENT
from helpers.proxies_randomise import get_random_proxy

class BaseApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'ru-RU,ru;q=0.9,en-RU;q=0.8,en;q=0.7,en-US;q=0.6',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'fetch-mode': 'no-cors',
            'fetch-site': 'same-origin',
            'origin': 'https://fractal.unisat.io',
            'referer': 'https://fractal.unisat.io/',
            'user-agent': USER_AGENT,
            'x-appid': APP_ID,
            'x-front-version': FRONT_VERSION
        }
        self.timestamp = None

    def _update_request_headers(self, url, method, params=None, data=None, update_ts: bool = False):
        base_string = (self.base_url or "") + url
        base_string = base_string.replace(self.base_url, '')

        if method.lower() == "get":
            if params:
                query = "&".join([f"{k}={v}" for k, v in params.items()])
                separator = "&" if '?' in base_string else "?"
                base_string += f"{separator}{query}"
            base_string += "\n"
        elif method.lower() == "post":
            base_string += "\n"
            if data:
                base_string += json.dumps(data, separators=(',', ':'))

        self.timestamp = int(time.time())
        self.headers['X-Ts'] = str(self.timestamp)
        base_string += f"\n{self.timestamp}@#?.#{SECRET_KEY}"

        x_sign = hashlib.md5(base_string.encode()).hexdigest()
        cf_token = (
            ''.join(random.choices(string.ascii_lowercase + string.digits, k=6)) + x_sign[12:14] +
            ''.join(random.choices(string.ascii_lowercase + string.digits, k=8)) + 'u' +
            ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        )

        self.headers.update({
            'X-Sign': x_sign,
            'cf-token': cf_token,
        })

        if update_ts:
            self.headers.update({
                "x-ts": f"{int(time.time() + random.randint(2, 6))}",
            })

    async def make_request(self, method: str, url: str, params=None, data=None):
        proxy = get_random_proxy()
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=self.headers, params=params, data=data, proxy=proxy) as response:
                if response.status != 200:
                    text = await response.text()
                    raise Exception(f"HTTP {response.status}: {text}")
                return await response.json()
