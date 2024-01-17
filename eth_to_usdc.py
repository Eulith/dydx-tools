from utils import get_kms_signer
from eulith_web3.signing import construct_signing_middleware
from eulith_web3.eulith_web3 import EulithWeb3
from credentials import *
from eulith_web3.erc20 import TokenSymbol
from eulith_web3.swap import EulithSwapRequest


def eth_to_usdc(parser_args):
    amount = float(parser_args.amount)
    network_id = int(parser_args.network_id)
    if network_id != 1:
        raise Exception(
            "unsupported network_id, can only perform this operation on mainnet"
        )

    kms_signer = get_kms_signer()
    with EulithWeb3(
        "https://eth-main.eulithrpc.com/v0",
        eulith_token=EULITH_TOKEN,
        signing_middle_ware=construct_signing_middleware(kms_signer),
    ) as ew3:
        weth = ew3.v0.get_erc_token(TokenSymbol.WETH)
        deposit_tx = weth.deposit_eth(
            amount, {"from": kms_signer.address, "gas": 200000}
        )
        tx_hash = ew3.eth.send_transaction(deposit_tx)
        print(f"Deposit tx hash {tx_hash.hex()} for amount: {amount} ETH")

        usdc = ew3.v0.get_erc_token(TokenSymbol.USDC)

        swap_request = EulithSwapRequest(
            sell_token=weth, buy_token=usdc, sell_amount=amount
        )
        price, txs = ew3.v0.get_swap_quote(swap_request)
        print(f"Swapping ETH to USDC at price: ${1 / price}")
        ew3.v0.send_multi_transaction(txs)

        print("Done swapping ETH to USDC")
