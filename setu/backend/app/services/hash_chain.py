"""
Tamper-evidence via hash chaining. Each record's hash includes the previous
record's hash, so altering an old record breaks every hash that follows it.
"""

import hashlib
import json


def compute_record_hash(record: dict, previous_hash: str) -> str:
    """TODO: confirm exact field ordering/serialization with the team before
    relying on this — the hash must be computed identically on-device and
    server-side, or chains won't match."""
    payload = json.dumps(record, sort_keys=True) + previous_hash
    return hashlib.sha256(payload.encode()).hexdigest()
