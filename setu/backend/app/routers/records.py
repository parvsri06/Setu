"""POST /records/batch — receives a batch of synced records from a bridge phone."""

from fastapi import APIRouter
from app.models import RecordBatchIn, RecordBatchResult

router = APIRouter(prefix="/records", tags=["records"])


@router.post("/batch", response_model=RecordBatchResult)
def ingest_batch(batch: RecordBatchIn):
    """
    TODO:
    1. For each record, call is_duplicate() — skip if already present.
    2. Verify/compute the hash chain.
    3. Insert into `records` (and `devices` if device_id is new).
    4. Return accepted / duplicates_skipped counts.
    """
    raise NotImplementedError
