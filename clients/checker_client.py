import json
from clients.base_client import BaseApiClient
from helpers.bitcoin_message_tool import sign_message
from helpers.logger import logger

class CheckerClient(BaseApiClient):
    def __init__(self, base_url: str, private_key_wif: str, address: str, pubkey: str):
        super().__init__(base_url)
        self.private_key = private_key_wif
        self.address = address
        self.public_key = pubkey
        self.session = None

    async def login(self):
        url = f"{self.base_url}/basic-v4/base/preload"
        params = {'address': self.address}
        self._update_request_headers(url='/basic-v4/base/preload', method='get', params=params)
        preload_response = await self.make_request(method='GET', url=url, params=params)

        if preload_response.get('code') != 0:
            raise Exception(f"Preload failed: {preload_response.get('msg')}")

        msg = preload_response['data']['signMsg']
        _, _, signature = sign_message(self.private_key, 'p2pkh', msg)

        login_url = f"{self.base_url}/basic-v4/base/login"
        data = {
            'address': self.address,
            'pubkey': self.public_key,
            'sign': signature,
            'walletType': 'unisat',
        }

        self._update_request_headers(url='/basic-v4/base/login', method='post', data=data)
        login_response = await self.make_request(method='POST', url=login_url, data=json.dumps(data, separators=(',', ':')))

        if login_response.get('code') != 0:
            raise Exception(f"Login failed: {login_response.get('msg')}")

        self.session = login_response['data']['session']
        self.headers.update({'unisat-session': self.session})
        points = login_response['data']['inscribeCount']
        logger.info(f'{self.address} has {points} points')
