"""
Dedup logic for batch ingestion.

A record's (device_id, local_counter) pair is its unique key. If a record
with that key already exists centrally, skip it silently — don't error,
since duplicate pushes from overlapping bridge phones are expected, not a bug.
"""


def is_duplicate(session, record_id: str) -> bool:
    """TODO: query the records table for an existing row with this id."""
    raise NotImplementedError
