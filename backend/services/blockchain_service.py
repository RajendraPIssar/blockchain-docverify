"""
services/blockchain_service.py
-------------------------------
Connects to the Hardhat local Ethereum node using Web3.py.
Calls our DocumentRegistry smart contract to register and verify hashes.
"""

import os
from web3 import Web3

# ── Configuration ─────────────────────────────────────────────────────────────
# These are read from environment variables set in .env
RPC_URL          = os.getenv("WEB3_URL",          "http://127.0.0.1:8545")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS",  "")
PRIVATE_KEY      = os.getenv("PRIVATE_KEY",       "")

# ABI — tells Web3 what functions the contract has
CONTRACT_ABI = [
    {
        "inputs": [
            {"internalType": "bytes32", "name": "docHash", "type": "bytes32"},
            {"internalType": "string",  "name": "meta",    "type": "string"}
        ],
        "name": "registerDocument",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "docHash", "type": "bytes32"}],
        "name": "verifyDocument",
        "outputs": [
            {"internalType": "bool",    "name": "", "type": "bool"},
            {"internalType": "uint256", "name": "", "type": "uint256"},
            {"internalType": "address", "name": "", "type": "address"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]


def _get_contract():
    """Connect to Hardhat node and return the contract object."""
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        raise ConnectionError(f"Cannot connect to blockchain at {RPC_URL}")
    if not CONTRACT_ADDRESS:
        raise ValueError("CONTRACT_ADDRESS not set in .env")
    return w3, w3.eth.contract(
        address=Web3.to_checksum_address(CONTRACT_ADDRESS),
        abi=CONTRACT_ABI
    )


def _hex_to_bytes32(hex_hash: str) -> bytes:
    """Convert a 64-char hex SHA-256 string to 32 raw bytes for Solidity."""
    return bytes.fromhex(hex_hash)


def register_on_chain(doc_hash: str, meta: str = "") -> dict:
    """
    Write the document hash to the blockchain.
    This costs gas (ETH) and creates an immutable record.
    Returns the transaction hash and block number.
    """
    w3, contract = _get_contract()
    account = w3.eth.account.from_key(PRIVATE_KEY)
    nonce   = w3.eth.get_transaction_count(account.address)

    txn = contract.functions.registerDocument(
        _hex_to_bytes32(doc_hash), meta
    ).build_transaction({
        "from":     account.address,
        "nonce":    nonce,
        "gas":      150000,
        "gasPrice": w3.eth.gas_price,
    })

    signed  = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)

    return {
        "tx_hash":      tx_hash.hex(),
        "block_number": receipt.blockNumber,
    }


def verify_on_chain(doc_hash: str) -> dict:
    """
    Query the smart contract for a document hash.
    This is a view function — completely FREE, no gas, no transaction.
    Returns exists (bool), timestamp (int), uploader (address).
    """
    w3, contract = _get_contract()
    exists, timestamp, uploader = contract.functions.verifyDocument(
        _hex_to_bytes32(doc_hash)
    ).call()

    return {
        "exists":    exists,
        "timestamp": timestamp,
        "uploader":  uploader,
    }
