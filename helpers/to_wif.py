import hashlib
import base58

def private_key_to_wif(private_key_hex: str, compressed=True, testnet=False) -> str:
    private_key = bytes.fromhex(private_key_hex)

    prefix = b'\x80'
    extended_key = prefix + private_key

    if compressed:
        extended_key += b'\x01'

    checksum = hashlib.sha256(hashlib.sha256(extended_key).digest()).digest()[:4]
    wif = base58.b58encode(extended_key + checksum).decode()
    return wif
