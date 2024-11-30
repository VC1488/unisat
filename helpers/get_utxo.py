import aiohttp
import asyncio

from config.settings import FRACTAL_API_KEY, FRACTAL_OPEN_API_URL
from helpers.proxies_randomise import get_random_proxy


async def get_utxo(address: str):
    url = f"{FRACTAL_OPEN_API_URL}/v1/indexer/address/{address}/utxo-data"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {FRACTAL_API_KEY}",
    }

    proxy = get_random_proxy()

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers, proxy=proxy) as response:
                if response.status == 200:
                    data = await response.json()
                    utxos = data.get("data", {}).get("utxo", [])
                    return utxos
                else:
                    text = await response.text()
                    raise Exception(f"Ошибка при получении UTXO: {text}")
        except aiohttp.ClientError as e:
            raise Exception(f"HTTP запрос не удался: {e}") from e
