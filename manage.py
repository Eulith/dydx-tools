import argparse

from accounts import get_account, register_user, show_wallet, create_user
from eth_to_usdc import eth_to_usdc
from exceptions import BadJurisdictionException
from funding import (
    approve_exchange_contract,
    get_transfers,
    deposit_to_dydx,
    start_withdraw_from_dydx,
    execute_withdraws,
)
from utils import check_ip_location

"""
To create and fund a new DyDx account, you must do the following:

1. Create User (`python manage.py create-user --network-id 1`)
2. Register User (`python manage.py register-user --network-id 1`)
3. Make sure you have some USDC (`python manage.py eth-to-usdc --amount 0.01 --network-id 1`)
4. Approve the DyDx exchange contract to take your USDC (`python manage.py approve-dydx-exchange --amount 25 --network-id 1`)
5. Deposit USDC to the exchange contract (`python manage.py deposit-dydx --amount 25 --network-id 1`)
"""


def main():
    parser = argparse.ArgumentParser(prog="dydx management cli")
    subparsers = parser.add_subparsers(help="all available dydx commands")

    #### show-wallet ####
    parser_show_wallet = subparsers.add_parser(
        "show-wallet", help="get the details of the configured eth wallet"
    )
    parser_show_wallet.set_defaults(func=show_wallet)

    #### create-user ####
    parser_create_user = subparsers.add_parser(
        "create-user", help="create a new dydx account"
    )
    parser_create_user.add_argument(
        "--network-id", help="the dydx network id (either 1 or 11155111)", required=True
    )
    parser_create_user.set_defaults(func=create_user)

    #### approve-dydx-exchange ####
    parser_greet = subparsers.add_parser(
        "approve-dydx-exchange",
        help="approve USDC to be taken by dydx exchange contract",
    )
    parser_greet.add_argument(
        "--network-id", help="the dydx network id (either 1 or 11155111)", required=True
    )
    parser_greet.add_argument(
        "--amount", help="the amount of USDC to approve", required=True
    )
    parser_greet.set_defaults(func=approve_exchange_contract)

    #### eth-to-usdc ####
    parser_greet = subparsers.add_parser(
        "eth-to-usdc",
        help="convert eth to usdc for depositing to dydx",
    )
    parser_greet.add_argument(
        "--network-id", help="the dydx network id (either 1 or 11155111)", required=True
    )
    parser_greet.add_argument(
        "--amount", help="the amount of USDC to approve", required=True
    )
    parser_greet.set_defaults(func=eth_to_usdc)

    #### get-account ####
    parser_get_account = subparsers.add_parser(
        "get-account", help="get the details of the configured dydx account"
    )
    parser_get_account.add_argument(
        "--network-id", help="the dydx network id (either 1 or 11155111)", required=True
    )
    parser_get_account.set_defaults(func=get_account)

    #### get-transfers ####
    parser_get_account = subparsers.add_parser(
        "get-transfers", help="get pending transfers to dydx"
    )
    parser_get_account.add_argument(
        "--network-id", help="the dydx network id (either 1 or 11155111)", required=True
    )
    parser_get_account.set_defaults(func=get_transfers)

    #### register-user ####
    parser_register_user = subparsers.add_parser(
        "register-user", help="register the user for trading"
    )
    parser_register_user.add_argument(
        "--network-id", help="the dydx network id (either 1 or 11155111)", required=True
    )
    parser_register_user.set_defaults(func=register_user)

    #### deposit-dydx ####
    parser_deposit_dydx = subparsers.add_parser(
        "deposit-dydx", help="deposit USDC into dydx"
    )
    parser_deposit_dydx.add_argument(
        "--network-id", help="the dydx network id (either 1 or 11155111)", required=True
    )
    parser_deposit_dydx.add_argument(
        "--amount", help="the amount of USDC to deposit", required=True
    )
    parser_deposit_dydx.set_defaults(func=deposit_to_dydx)

    #### start-withdraw-dydx ####
    parser_withdraw = subparsers.add_parser(
        "start-withdraw-dydx", help="initiate a fast withdraw in USDC from dydx"
    )
    parser_withdraw.add_argument(
        "--network-id", help="the dydx network id (either 1 or 11155111)", required=True
    )
    parser_withdraw.add_argument(
        "--amount", help="the amount of USDC to withdraw", required=True
    )
    parser_withdraw.set_defaults(func=start_withdraw_from_dydx)

    #### execute-withdraws ####
    parser_execute_withdraws = subparsers.add_parser(
        "execute-withdraws", help="initiate a fast withdraw in USDC from dydx"
    )
    parser_execute_withdraws.add_argument(
        "--network-id", help="the dydx network id (either 1 or 11155111)", required=True
    )
    parser_execute_withdraws.set_defaults(func=execute_withdraws)

    # Parse the arguments
    args = parser.parse_args()

    # Execute the function associated with the chosen subcommand
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    try:
        print("Checking whether you're calling from a safe IP location...")
        check_ip_location()
        print("Looks good, proceeding.")
        print()
    except BadJurisdictionException as e:
        print(e)
        exit(1)
    except Exception as e:
        print(
            "Could not determine your IP location, unsafe to proceed with DyDx operations. Terminating."
        )
        exit(1)

    main()
