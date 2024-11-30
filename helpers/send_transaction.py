from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.keys import PublicKey, PrivateKey
from bitcoinutils.setup import setup
from helpers.get_btc_address import get_btc_address
from helpers.logger import logger

async def send_btc(
    public_key: PublicKey,
    private_key: PrivateKey,
    destination_address: str,
    amount: int,
    miner_fee: int = 0,
    return_tx_size: bool = False,
    taproot_address: bool = True,
    broadcast_func=None,
    select_utxos_func=None,
    silent_mode: bool = False,
) -> bool | int:

    setup('mainnet')

    from_address = public_key.get_taproot_address()
    to_address = get_btc_address(destination_address)

    selected_utxos, utxos_total_amount, full_balance = await select_utxos_func(from_address.to_string(), amount, miner_fee)
    if not selected_utxos or utxos_total_amount < amount + miner_fee:
        if logger:
            logger.error(f"Не удалось найти подходящие UTXO или недостаточный баланс.")
        return False

    if not return_tx_size and not silent_mode and logger:
        logger.info(f"Баланс: {full_balance} сатоши. Отправка {amount} сатоши на {destination_address}.")

    change_amount = utxos_total_amount - amount - miner_fee
    if change_amount < 0:
        raise Exception("Недостаточный баланс.")

    tx_inputs = [TxInput(utxo['txid'], utxo['vout']) for utxo in selected_utxos]
    tx_outputs = [
        TxOutput(amount, to_address.to_script_pub_key()),
        TxOutput(change_amount, from_address.to_script_pub_key())
    ]

    tx = Transaction(tx_inputs, tx_outputs, has_segwit=True)

    utxos_script_pubkeys = [from_address.to_script_pub_key() for _ in selected_utxos]
    selected_utxo_values = [int(utxo['satoshi']) for utxo in selected_utxos]

    for i, txin in enumerate(tx_inputs):
        if taproot_address:
            sig = private_key.sign_taproot_input(
                tx,
                i,
                utxos_script_pubkeys,
                selected_utxo_values,
                script_path=False
            )
            tx.witnesses.append(TxWitnessInput([sig]))
        else:
            script_code = from_address.to_script_pub_key()
            sig = private_key.sign_segwit_input(tx, i, script_code, selected_utxo_values[i])
            tx.witnesses.append(TxWitnessInput([sig, public_key.to_hex()]))

    if return_tx_size:
        return tx.get_size()

    signed_tx = tx.serialize()

    try:
        if broadcast_func:
            return await broadcast_func(signed_tx)
        else:
            raise ValueError("Функция отправки транзакции не предоставлена.")
    except Exception as error:
        if 'too-long-mempool-chain' in str(error):
            raise Exception("Мемпул переполнен. Попробуйте позже.")
        raise Exception(f"Ошибка отправки транзакции: {error}")
