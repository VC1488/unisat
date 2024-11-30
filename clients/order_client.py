import json
from clients.base_client import BaseApiClient


class OrderClient(BaseApiClient):
    def __init__(self, base_url: str):
        super().__init__(base_url)

    async def create_order(self, session: str, data: dict):
        url = '/inscribe-v5/order/create'
        full_url = self.base_url + url

        self.headers.update({'unisat-session': session})
        self._update_request_headers(url='/inscribe-v5/order/create', method='post', data=data)
        response = await self.make_request(method='POST', url=full_url, data=json.dumps(data, separators=(',', ':')))



        return response
