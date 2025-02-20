#!/usr/bin/env python3
"""
generate_usdt_wallet.py

This script uses TronPy to generate a TRON wallet address capable of receiving TRC-20 tokens like USDT.
It defines a class USDTWallet that creates a private/public key pair and derives the address.
"""

from tronpy.keys import PrivateKey

class USDTWallet:
    def __init__(self):
        """
        Generate a random private key and derive the corresponding
        TRON (public) address. This address can hold both TRX and TRC-20 tokens.
        """
        self._private_key = PrivateKey.random()
        self._public_key = self._private_key.public_key
        self._address = self._public_key.to_base58check_address()

    def get_private_key_hex(self):
        """
        Returns the private key in hex string format.
        Keep this PRIVATE and secure. Anyone with this key can control your funds.
        """
        return self._private_key.hex()

    def get_public_address(self):
        """
        Returns the TRON public address (which starts with 'T').
        This address can receive TRX or any TRC-20 token (including USDT).
        """
        return self._address


if __name__ == "__main__":
    # Example usage
    wallet = USDTWallet()

    print("=== New USDT Wallet Generated ===")
    print("Private Key (Hex):", wallet.get_private_key_hex())
    print("Public TRON Address:", wallet.get_public_address())
    print("\nRemember to store your private key safely offline.")

