import base64
import hashlib
import hmac

from dydx3.helpers.request_helpers import generate_now_iso, json_stringify
from dydx3.helpers.request_helpers import remove_nones
from dydx3.helpers.requests import request
from credentials import *


def generate_request_signature(
    request_path: str, method: str, iso_timestamp: str, data: dict
) -> str:
    message_string = (
        iso_timestamp + method + request_path + (json_stringify(data) if data else "")
    )

    hashed = hmac.new(
        base64.urlsafe_b64decode(API_SECRET.encode("utf-8")),
        msg=message_string.encode("utf-8"),
        digestmod=hashlib.sha256,
    )
    return base64.urlsafe_b64encode(hashed.digest()).decode()


def private_request(host, method, endpoint, data={}):
    now_iso_string = generate_now_iso()
    request_path = "/".join(["/v3", endpoint])
    signature = generate_request_signature(
        request_path=request_path,
        method=method.upper(),
        iso_timestamp=now_iso_string,
        data=remove_nones(data),
    )

    headers = {
        "DYDX-SIGNATURE": signature,
        "DYDX-API-KEY": API_KEY,
        "DYDX-TIMESTAMP": now_iso_string,
        "DYDX-PASSPHRASE": API_PASSPHRASE,
    }

    return request(host + request_path, method, headers, data, 30).data
