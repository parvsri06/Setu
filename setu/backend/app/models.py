"""
Pydantic request/response models — the API contract.
Canonical field definitions live in ../shared/record_schema.json — keep this in sync with it.
"""

from pydantic import BaseModel
from typing import Optional, List


class SurveyData(BaseModel):
    name: str
    household_size: Optional[int] = None
    notes: Optional[str] = None


class RecordIn(BaseModel):
    """A single record as pushed by a bridge phone."""
    id: str                 # device_id:local_counter
    device_id: str
    local_counter: int
    captured_at: str        # ISO 8601
    latitude: float
    longitude: float
    survey_data: SurveyData
    record_hash: str


class RecordBatchIn(BaseModel):
    records: List[RecordIn]


class RecordBatchResult(BaseModel):
    accepted: int
    duplicates_skipped: int
