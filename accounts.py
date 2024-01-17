from dydx3 import private_key_to_public_key_pair_hex
from dydx3.constants import *
from dydx3.eth_signing.eth_prive_action import SignEthPrivateAction
from dydx3.eth_signing.onboarding_action import SignOnboardingAction
from dydx3.helpers.request_helpers import generate_now_iso
from dydx3.helpers.requests import request
from eulith_web3.signer import Signer, Signature
from eulith_web3.signing import construct_signing_middleware
from eulith_web3.eulith_web3 import EulithWeb3

from credentials import *
from private_request import private_request
from utils import get_dydx_host, get_exchange_contract, get_kms_signer


def normalize_signature(signature: Signature) -> str:
    """
    Normalize the signature to a string, for instance for serialization for an RPC method.
    """
    compatible_v = signature.v + 27
    last_two_chars = hex(compatible_v)[-2:]
    return str(signature)[:-2] + last_two_chars


def create_user(parser_args):
    network_id = int(parser_args.network_id)
    signer = get_kms_signer()
    host = get_dydx_host(network_id)

    public_x, public_y = private_key_to_public_key_pair_hex(STARK_PRIVATE_KEY)

    sign_offchain_action = SignOnboardingAction(signer, NETWORK_ID_MAINNET)
    message = {
        "action": OFF_CHAIN_ONBOARDING_ACTION,
    }
    message_hash = sign_offchain_action.get_hash(**message)
    signature = signer.sign_msg_hash(message_hash)
    ns = (
        normalize_signature(signature) + "00"
    )  # // 00 comes from SIGNATURE_TYPE_NO_PREPEND in constants

    request_path = "/".join(["/v3", "onboarding"])
    response = request(
        host + request_path,
        "post",
        {
            "DYDX-SIGNATURE": ns,
            "DYDX-ETHEREUM-ADDRESS": signer.address,
        },
        {
            "starkKey": public_x,
            "starkKeyYCoordinate": public_y,
        },
        10,
    ).data

    print(f"Created user, response:")
    print(response)
    print()
    print("YOU SHOULD WRITE DOWN THESE API CREDENTIALS")


def get_account(parser_args):
    network_id = int(parser_args.network_id)
    print(_get_account_internal(network_id))


def _get_account_internal(network_id: int) -> dict:
    host = get_dydx_host(network_id)
    response = private_request(host, "get", "accounts", {})
    return response.get("accounts", {})[
        0
    ]  # dydx appears to only supports 1 account per eth key


def get_registration_signature(network_id: int) -> dict:
    host = get_dydx_host(network_id)
    response = private_request(host, "get", "registration", {})
    return response.get("signature")


def create_new_api_key_with_signer(signer: Signer, network_id: int):
    host = get_dydx_host(network_id)

    sign_offchain_action = SignEthPrivateAction(signer, NETWORK_ID_MAINNET)
    request_path = "/".join(["/v3", "api-keys"])
    timestamp = generate_now_iso()

    message = {
        "method": "POST",
        "request_path": request_path,
        "body": "{}",
        "timestamp": timestamp,
    }
    message_hash = sign_offchain_action.get_hash(**message)
    signature = signer.sign_msg_hash(message_hash)
    ns = (
        normalize_signature(signature) + "00"
    )  # // 00 comes from SIGNATURE_TYPE_NO_PREPEND in constants

    return request(
        host + request_path,
        "post",
        {
            "DYDX-SIGNATURE": ns,
            "DYDX-TIMESTAMP": timestamp,
            "DYDX-ETHEREUM-ADDRESS": signer.address,
        },
        {},
        10,
    ).data


def register_user(parser_args):
    network_id = int(parser_args.network_id)
    if network_id != 1:
        raise ValueError("only mainnet is supported for now")

    public_x, public_y = private_key_to_public_key_pair_hex(STARK_PRIVATE_KEY)

    reg_signature = get_registration_signature(network_id)
    kms_signer = get_kms_signer()

    with EulithWeb3(
        "https://eth-main.eulithrpc.com/v0",
        eulith_token=EULITH_TOKEN,
        signing_middle_ware=construct_signing_middleware(kms_signer),
    ) as ew3:
        contract = get_exchange_contract(network_id, ew3)

        tx_params = contract.functions.registerUser(
            kms_signer.address, int(public_x, 16), reg_signature
        ).buildTransaction({"from": kms_signer.address, "gas": 100000})

        tx_hash = ew3.eth.send_transaction(tx_params)
        print(f"Registration tx hash: {tx_hash.hex()}")


def show_wallet(_args):
    signer = get_kms_signer()
    print(f"wallet address: {signer.address}")
