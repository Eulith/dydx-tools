import json
from datetime import datetime, timedelta

import boto3
import requests
from dydx3.constants import *
from eulith_web3.kms import KmsSigner
from eulith_web3.signer import Signer
from web3 import Web3

from credentials import *
from exceptions import BadJurisdictionException


def get_exchange_contract_address(network_id: int):
    return STARKWARE_PERPETUALS_CONTRACT.get(network_id)


def get_dydx_host(network_id: int):
    if network_id == NETWORK_ID_MAINNET:
        return "https://api.dydx.exchange"
    elif network_id == NETWORK_ID_SEPOLIA:
        return "https://api.stage.dydx.exchange"
    else:
        raise Exception("unsupported network_id")


def get_exchange_contract(network_id: int, web3: Web3):
    contract_address = get_exchange_contract_address(network_id)

    return web3.eth.contract(
        address=contract_address,
        abi=json.load(open("abi/starkware-perpetuals.json", "r")),
    )


def get_kms_signer() -> Signer:
    aws_credentials_profile_name = AWS_CREDENTIALS_PROFILE_NAME
    formatted_key_name = f"alias/{ETH_SIGNER_KEY_NAME}"

    session = boto3.Session(profile_name=aws_credentials_profile_name)
    client = session.client("kms")

    kms_signer = KmsSigner(client, formatted_key_name)
    return kms_signer


def now_timestamp_plus_minutes(minutes: int) -> str:
    now = datetime.utcnow()
    future_time = now + timedelta(minutes=minutes)
    timestamp = future_time.strftime("%Y-%m-%dT%H:%M:%S") + ".{:03d}Z".format(
        int(future_time.microsecond / 1000)
    )

    return timestamp


def check_ip_location():
    response = requests.get("https://ipinfo.io/json").json()
    timezone = response.get("timezone")
    if "Europe" not in timezone:
        raise BadJurisdictionException(
            "If you make a request from a blocked jurisdiction, "
            "dydx will permanently ban you and shut down your account. "
            "Shutting down now to prevent this."
        )
