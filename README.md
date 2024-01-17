# DyDx Account Management
The open source DyDx Client libraries do not provide adequate support for the security infrastructure
of institutional clients. For example, it forces you to use a plain-text ETH signing key with a deterministic
signing algorithm. This is woefully inadequate for any risk-conscious user.

This library provides a simple way to manage your DyDx account with institutional-grade ETH signatures from AWS KMS.

It also provides some nice tooling for getting in and out of compatible assets for collateral deposits.

# Usage
You need to edit the values in `credentials.py` to use this library.

If you have questions, reach out to engineers@eulith.com.

To create and fund a new DyDx account, you must do the following:

1. Create User (`python manage.py create-user --network-id 1`)
2. Register User (`python manage.py register-user --network-id 1`)
3. Make sure you have some USDC (`python manage.py eth-to-usdc --amount 0.01 --network-id 1`)
4. Approve the DyDx exchange contract to take your USDC (`python manage.py approve-dydx-exchange --amount 25 --network-id 1`)
5. Deposit USDC to the exchange contract (`python manage.py deposit-dydx --amount 25 --network-id 1`)