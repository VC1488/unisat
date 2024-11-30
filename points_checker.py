import json
import asyncio
import aiofiles
from clients.checker_client import CheckerClient
from config.settings import BASE_URL
from helpers.logger import logger

async def read_wallets(file_path: str):
    async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
        content = await f.read()
        wallets = json.loads(content)
    return wallets

async def process_single_wallet(wallet_name: str, wallet_info: dict, semaphore: asyncio.Semaphore):
    async with semaphore:
        try:
            login_client = CheckerClient(
                base_url=BASE_URL,
                private_key_wif=wallet_info['private_key_wif'],
                address=wallet_info['address'],
                pubkey=wallet_info['public_key']
            )
            await login_client.login()

        except Exception as e:
            logger.error(f"Кошелек {wallet_name} - Ошибка: {e}")

async def checker(file_path: str, batch_size: int = 5):
    wallets = await read_wallets(f'{file_path}')
    semaphore = asyncio.Semaphore(batch_size)
    tasks = []

    for wallet_name, wallet_info in wallets.items():
        task = asyncio.create_task(process_single_wallet(wallet_name, wallet_info, semaphore))
        tasks.append(task)

    await asyncio.gather(*tasks)
    logger.info("Все кошельки обработаны.")

file_path = 'data/wallet_info.json'

asyncio.run(checker(file_path))