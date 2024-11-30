from helpers.get_utxo import get_utxo

async def select_utxos(address: str, amount: int, miner_fee: int) -> tuple[list[dict], int, int]:
    utxos = await get_utxo(address)

    available_utxos = [utxo for utxo in utxos if not utxo.get("isSpent", False)]

    wallet_balance = sum(utxo.get("satoshi", 0) for utxo in available_utxos)

    required_amount = amount + miner_fee
    if wallet_balance < required_amount:
        raise Exception(
            f"Недостаточно средств: доступно {wallet_balance} сатоши, "
            f"требуется {required_amount} сатоши."
        )

    available_utxos.sort(key=lambda x: x.get("satoshi", 0))

    selected_utxos = []
    selected_amount = 0

    for utxo in available_utxos:
        selected_utxos.append({
            "txid": utxo["txid"],
            "vout": utxo["vout"],
            "satoshi": utxo["satoshi"],
        })
        selected_amount += utxo["satoshi"]

        if selected_amount >= required_amount:
            break

    if selected_amount < required_amount:
        raise Exception(
            f"Недостаточно выбранных средств: выбрано {selected_amount} сатоши, "
            f"требуется {required_amount} сатоши."
        )

    return selected_utxos, selected_amount, wallet_balance
