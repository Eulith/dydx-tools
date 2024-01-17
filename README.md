# DyDx Account Management
The open source DyDx Client libraries do not provide adequate support for the security infrastructure
of institutional clients. For example, it forces you to use a plain-text ETH signing key with a deterministic
signing algorithm. This is woefully inadequate for any risk-conscious user.

This library provides a simple way to manage your DyDx account with institutional-grade ETH signatures from AWS KMS.

It also provides some nice tooling for getting in and out of compatible assets for collateral deposits.

# Usage
You need to edit the values in `credentials.py` to use this library.

If you have questions, reach out to engineers@eulith.com.