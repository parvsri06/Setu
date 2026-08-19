"""Verified-list export (Phase 7): CSV download, Aadhaar masked, audit-logged.

Columns are PROVISIONAL pending the final SDRF/DBT form decision (design.md §9 #2).
Only surveys that have been synced are exported; Aadhaar is masked to its last 4
digits in the output (raw value is never emitted).
"""
from __future__ import annotations

import csv
import io
import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import ExportLog, Survey, User
from ..security import mask_aadhaar, require_dev

router = APIRouter(prefix="/api/v1", tags=["export"])


EXPORT_COLUMNS = [
    "survey_number",
    "unique_id",
    "full_name",
    "father_name",
    "mobile",
    "aadhaar_masked",
    "district",
    "village_town",
    "disaster_type",
    "damage_date",
    "camp_name",
    "person_name",
    "person_age",
    "person_gender",
    "person_status",
    "current_location",
    "collected_at",
    "verified_by",
]


def _build_csv(db: Session, exported_by: str) -> tuple[str, int]:
    stmt = (
        select(Survey)
        .join(User)
        .where(Survey.is_synced.is_(True))
        .order_by(Survey.survey_number.asc())
    )
    surveys = db.scalars(stmt).all()

    buf = io.StringIO()
    buf.write("\ufeff")  # UTF-8 BOM for Excel
    writer = csv.writer(buf)
    writer.writerow(EXPORT_COLUMNS)

    rows = 0
    for s in surveys:
        for c in s.casualties:
            writer.writerow(
                [
                    s.survey_number or "",
                    str(s.survey_id),
                    s.user.full_name,
                    s.user.father_name,
                    s.user.mobile_number,
                    mask_aadhaar(s.user.aadhaar_number),
                    s.district,
                    s.village,
                    s.disaster_type,
                    s.damage_date.isoformat() if s.damage_date else "",
                    s.relief_camp.camp_name if s.relief_camp else "",
                    c.person_name,
                    c.age,
                    c.gender,
                    c.status,
                    c.current_location,
                    s.created_at.isoformat() if s.created_at else "",
                    exported_by,
                ]
            )
            rows += 1

    # Audit the export (original audit_logs only tracks status changes).
    db.add(ExportLog(exported_by=exported_by, row_count=rows, note="verified csv"))
    db.commit()
    return buf.getvalue(), rows


@router.get("/export/verified")
def export_verified(
    db: Session = Depends(get_db),
    actor: str = Depends(require_dev),
) -> StreamingResponse:
    csv_text, _ = _build_csv(db, exported_by=actor)
    return StreamingResponse(
        iter([csv_text]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=verified_registry.csv"},
    )
