from time import sleep
from typing import List

from dydx3 import private_key_to_public_key_pair_hex
from dydx3.constants import *
from dydx3.helpers.request_helpers import random_client_id, iso_to_epoch_seconds
from dydx3.starkex.withdrawal import SignableWithdrawal
from eulith_web3.erc20 import EulithERC20
from eulith_web3.eulith_web3 import EulithWeb3
from eulith_web3.signing import construct_signing_middleware

from accounts import _get_account_internal
from credentials import *
from private_request import private_request
from utils import (
    get_exchange_contract_address,
    get_kms_signer,
    get_exchange_contract,
    get_dydx_host,
    now_timestamp_plus_minutes,
)


def approve_exchange_contract(args):
    network_id = int(args.network_id)
    amount = float(args.amount)

    if network_id != 1:
        raise Exception("unsupported network_id, can only approve on mainnet")

    kms_signer = get_kms_signer()
    print(f"Executing from eth address: {kms_signer.address}")

    with EulithWeb3(
        "https://eth-main.eulithrpc.com/v0",
        eulith_token=EULITH_TOKEN,
        signing_middle_ware=construct_signing_middleware(kms_signer),
    ) as ew3:
        usdc_address = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
        contract = EulithERC20(ew3, ew3.to_checksum_address(usdc_address))
        spender = get_exchange_contract_address(network_id)

        approve_tx = contract.approve_float(
            spender, amount, {"from": kms_signer.address, "gas": 200000}
        )
        tx_hash = ew3.eth.send_transaction(approve_tx)
        print(f"Approve tx hash {tx_hash.hex()} for amount: {amount} USDC")


def get_transfers(args):
    network_id = int(args.network_id)
    transfers = _get_transfers_internal(network_id)
    for t in transfers:
        print(t)


def _get_transfers_internal(network_id: int) -> List:
    host = get_dydx_host(network_id)

    response = private_request(host, "get", "transfers")
    return response.get("transfers")


def deposit_to_dydx(args):
    network_id = int(args.network_id)
    amount = float(args.amount)

    if network_id != 1:
        raise Exception("unsupported network_id, can only deposit on mainnet")

    kms_signer = get_kms_signer()
    print(f"Executing from eth address: {kms_signer.address}")

    with EulithWeb3(
        "https://eth-main.eulithrpc.com/v0",
        eulith_token=EULITH_TOKEN,
        signing_middle_ware=construct_signing_middleware(kms_signer),
    ) as ew3:
        contract = get_exchange_contract(network_id, ew3)

        public_x, public_y = private_key_to_public_key_pair_hex(STARK_PRIVATE_KEY)
        account = _get_account_internal(network_id)
        position_id = account.get("positionId")

        tx_params = contract.functions.deposit(
            int(public_x, 16),
            COLLATERAL_ASSET_ID_BY_NETWORK_ID[network_id],
            int(position_id),
            int(float(amount) * float(ASSET_RESOLUTION[COLLATERAL_ASSET])),
        ).buildTransaction({"from": kms_signer.address, "gas": 200000})

        tx_hash = ew3.eth.send_transaction(tx_params)
        print(f"Deposit to DyDx tx hash: {tx_hash.hex()}")
        print()

        print("Fetching transfers into dydx...")
        attempt = 0

        while attempt < 5:
            attempt += 1
            transfers = _get_transfers_internal(network_id)
            if len(transfers) == 0:
                sleep(2)
                continue
            else:
                print(transfers)


def start_withdraw_from_dydx(args):
    network_id = int(args.network_id)
    amount = int(args.amount)
    print(f"Withdrawing amount: {amount} USDC")

    client_id = random_client_id()
    expiration = now_timestamp_plus_minutes(60 * 24 * 30)  # 30 days
    expiration_epoch_seconds = iso_to_epoch_seconds(expiration)

    account = _get_account_internal(network_id)
    position_id = account.get("positionId")

    withdrawal_to_sign = SignableWithdrawal(
        network_id=network_id,
        position_id=position_id,
        client_id=client_id,
        human_amount=str(amount),
        expiration_epoch_seconds=expiration_epoch_seconds,
    )
    signature = withdrawal_to_sign.sign(STARK_PRIVATE_KEY)

    params = {
        "amount": str(amount),
        "asset": "USDC",
        "expiration": expiration,
        "clientId": client_id,
        "signature": signature,
    }

    host = get_dydx_host(network_id)

    print("Withdraw response: ")
    print(private_request(host, "post", "withdrawals", params))


def execute_withdraws(args):
    network_id = int(args.network_id)
    kms_signer = get_kms_signer()

    with EulithWeb3(
        "https://eth-main.eulithrpc.com/v0",
        eulith_token=EULITH_TOKEN,
        signing_middle_ware=construct_signing_middleware(kms_signer),
    ) as ew3:
        contract = get_exchange_contract(network_id, ew3)

        public_x, public_y = private_key_to_public_key_pair_hex(STARK_PRIVATE_KEY)

        tx_params = contract.functions.withdraw(
            int(public_x, 16),
            COLLATERAL_ASSET_ID_BY_NETWORK_ID[network_id],
        ).buildTransaction({"from": kms_signer.address, "gas": 200000})

        tx_hash = ew3.eth.send_transaction(tx_params)
        print(f"Withdraw tx hash: {tx_hash.hex()}")
        print()
