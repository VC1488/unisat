import json
import asyncio
import aiofiles
from bitcoinutils.setup import setup

from clients.login_client import LoginClient
from clients.order_client import OrderClient
from helpers.get_words import get_words
from config.settings import BASE_URL
from helpers.logger import logger
from bitcoinutils.keys import PublicKey, PrivateKey
from helpers.broadcast_transaction import broadcast_transaction
from helpers.select_utxos import select_utxos
from helpers.send_transaction import send_btc

async def read_wallets(file_path: str):
    async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
        content = await f.read()
        wallets = json.loads(content)
    return wallets

async def process_single_wallet(wallet_name: str, wallet_info: dict, semaphore: asyncio.Semaphore):
    async with semaphore:
        try:
            login_client = LoginClient(
                base_url=BASE_URL,
                private_key_wif=wallet_info['private_key_wif'],
                address=wallet_info['address'],
                pubkey=wallet_info['public_key']
            )
            order_client = OrderClient(base_url=BASE_URL)

            await login_client.login()

            files = get_words()
            data = {
                "files": files,
                "receiver": wallet_info['address'],
                "feeRate": 2,
                "outputValue": 546,
                "clientId": f"client_{wallet_name}"
            }

            response = await order_client.create_order(session=login_client.session, data=data)
            logger.info(f"Кошелек {wallet_name} - Заказ создан: {response}")

            setup('mainnet')
            send_tx = await send_btc(
                public_key=PublicKey(wallet_info['public_key']),
                private_key=PrivateKey(wallet_info['private_key_wif']),
                destination_address=response['data']['payAddress'],
                amount=response['data']['amount'],
                miner_fee=response['data']['minerFee'],
                return_tx_size=False,
                taproot_address=True,
                broadcast_func=broadcast_transaction,
                select_utxos_func=select_utxos,
            )

            if send_tx:
                logger.info(f"Кошелек {wallet_name} - успешно отправлено. Результат: {send_tx}")
            else:
                logger.error(f"Кошелек {wallet_name} - Отправка BTC не удалась.")


        except Exception as e:
            logger.error(f"Кошелек {wallet_name} - Ошибка: {e}")

async def processor_wallet(file_path: str, batch_size: int = 5):
    wallets = await read_wallets(file_path)
    semaphore = asyncio.Semaphore(batch_size)
    tasks = []

    for wallet_name, wallet_info in wallets.items():
        task = asyncio.create_task(process_single_wallet(wallet_name, wallet_info, semaphore))
        tasks.append(task)

    await asyncio.gather(*tasks)
    logger.info("Все кошельки обработаны.")
