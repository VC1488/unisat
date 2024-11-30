import asyncio
from helpers.wallet_processor import processor_wallet

async def main():
    file_path = 'data/wallet_info.json'
    await processor_wallet(file_path, batch_size=5)

if __name__ == "__main__":
    asyncio.run(main())
