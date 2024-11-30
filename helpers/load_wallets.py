import json
from bip_utils import Bip39SeedGenerator, Bip86, Bip86Coins
from mnemonic import Mnemonic
from helpers.logger import logger
from helpers.to_wif import private_key_to_wif

def load_wallets():
    try:
        with open('data/mnemonic.txt', 'r') as f:
            mnemonics = f.readlines()

        mnemo = Mnemonic("english")
        wallet_info = {}

        for idx, mnemonic_phrase in enumerate(mnemonics, start=1):
            mnemonic_phrase = mnemonic_phrase.strip()

            if not mnemo.check(mnemonic_phrase):
                logger.warning(f"Mnemonic {idx} is not valid.")
                continue

            wallet_name = f"wallet_{idx}"

            try:
                seed = Bip39SeedGenerator(mnemonic_phrase).Generate()
                bip86_ctx = Bip86.FromSeed(seed, Bip86Coins.BITCOIN)
                account = bip86_ctx.DeriveDefaultPath()
                private_key_hex = account.PrivateKey().Raw().ToHex()
                private_key_wif = private_key_to_wif(private_key_hex, compressed=True, testnet=False)
                public_key_hex = account.PublicKey().RawCompressed().ToHex()
                address = account.PublicKey().ToAddress()

                logger.info(f"Wallet '{wallet_name}':")
                logger.info(f"Private Key (Hex): {private_key_hex}")
                logger.info(f"Private Key (WIF): {private_key_wif}")
                logger.info(f"Address: {address}")
                logger.info(f"Public Key: {public_key_hex}\n")

                wallet_info[wallet_name] = {
                    'private_key': private_key_hex,
                    'private_key_wif': private_key_wif,
                    'public_key': public_key_hex,
                    'address': address,
                    'mnemonic': mnemonic_phrase
                }

            except Exception as e:
                logger.warning(f"Error processing wallet '{wallet_name}': {e}\n")

        with open('../../UNISATTT/data/wallet_info.json', 'w') as f_out:
            json.dump(wallet_info, f_out, indent=4)
        logger.info("Wallets info is saved at 'wallet_info.json'.")

    except FileNotFoundError:
        logger.warning("File not found")
        raise
    except Exception as e:
        logger.warning(f"Unable to load wallets: {e}")
        raise



if __name__ == "__main__":
    load_wallets()
