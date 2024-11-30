from bitcoinutils.keys import P2trAddress, P2wpkhAddress, P2shAddress, P2pkhAddress


def get_btc_address(address: str):
    if address.startswith('bc1p'):
        return P2trAddress.from_address(address)
    elif address.startswith('bc1q'):
        return P2wpkhAddress.from_address(address)
    elif address.startswith('3'):
        return P2shAddress.from_address(address)
    elif address.startswith('1'):
        return P2pkhAddress.from_address(address)
    else:
        print("Soft support only P2TR (bc1p...) or P2WPKH (bc1q...) addresses")