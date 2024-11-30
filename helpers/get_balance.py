import asyncio
import json
import aiofiles

from helpers.get_utxo import get_utxo
from helpers.logger import logger
file_path = '../data/wallet_info.json'

async def read_wallets(file_path: str):
    async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
        content = await f.read()
        wallets = json.loads(content)
    return wallets

def get_balance(address: str) -> float:
    utxos = get_utxo(address)
    available_utxos = [utxo for utxo in utxos if not utxo["isSpent"]]
    wallet_balance = sum(utxo["satoshi"] for utxo in available_utxos)
    return wallet_balance / 10**8

async def print_balance(wallet_name: str, address: str):
    try:
        wallet_balance = await asyncio.to_thread(get_balance, address)
        logger.info(f'Кошелек: {wallet_name}\nАдрес: {address}\nБаланс: {wallet_balance:.8f} FB\n')
    except Exception as e:
        logger.warning(f'Скорее всего у коша нет UTXO {wallet_name} ({address}): {e}\n')

async def main():
    wallets = await read_wallets(file_path)
    tasks = []

    for wallet_name, wallet_info in wallets.items():
        address = wallet_info.get('address')
        if address:
            task = asyncio.create_task(print_balance(wallet_name, address))
            tasks.append(task)
        else:
            logger.warning(f'Кошелек {wallet_name} не содержит адреса.\n')

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
