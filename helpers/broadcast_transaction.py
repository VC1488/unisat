import aiohttp
import asyncio

from config.settings import FRACTAL_OPEN_API_URL, FRACTAL_API_KEY
from helpers.proxies_randomise import get_random_proxy


async def broadcast_transaction(signed_tx: str):
    API_URL = f"{FRACTAL_OPEN_API_URL}/v1/indexer/local_pushtx"
    API_KEY = FRACTAL_API_KEY

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    proxy = get_random_proxy()

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(API_URL, json={"txHex": signed_tx}, headers=headers, proxy=proxy) as response:
                if response.status == 200:
                    json_response = await response.json()
                    return json_response.get("data")
                else:
                    text = await response.text()
                    raise Exception(f"Error broadcasting transaction: {text}")
        except aiohttp.ClientError as e:
            raise Exception(f"HTTP request failed: {e}") from e
