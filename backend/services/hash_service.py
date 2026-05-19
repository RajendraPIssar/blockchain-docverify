"""
services/hash_service.py
------------------------
SHA-256 hashing of document bytes.
The hash is the document's unique fingerprint stored on the blockchain.
"""

import hashlib


def hash_bytes(file_bytes: bytes) -> str:
    """
    Compute SHA-256 hash of raw file bytes.
    Returns a 64-character lowercase hex string.
    Always the same output for the same input (deterministic).
    """
    return hashlib.sha256(file_bytes).hexdigest()
