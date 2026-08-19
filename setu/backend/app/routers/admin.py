"""Admin / dev endpoints (Phase 8): read-only dashboard + audit views.

Gated by require_dev (JWT or X-Dev-Key). "Revoke device" is intentionally
omitted — there is no responders/device table in the schema, so there is nothing
to revoke. These endpoints are for us (the builders) to inspect the registry.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import AuditLog, ExportLog, Survey, SyncLog, User
from ..security import require_dev

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/surveys")
def list_surveys(
    district: Optional[str] = Query(default=None),
    disaster_type: Optional[str] = Query(default=None),
    limit: int = Query(default=100, le=1000),
    db: Session = Depends(get_db),
    _: str = Depends(require_dev),
):
    stmt = select(Survey).join(User)
    if district:
        stmt = stmt.where(Survey.district == district)
    if disaster_type:
        stmt = stmt.where(Survey.disaster_type == disaster_type)
    stmt = stmt.order_by(Survey.created_at.desc()).limit(limit)
    surveys = db.scalars(stmt).all()
    return {
        "count": len(surveys),
        "surveys": [
            {
                "survey_number": s.survey_number,
                "survey_id": str(s.survey_id),
                "full_name": s.user.full_name,
                "mobile": s.user.mobile_number,
                "district": s.district,
                "village": s.village,
                "disaster_type": s.disaster_type,
                "damage_date": s.damage_date.isoformat() if s.damage_date else None,
                "survey_status": s.survey_status,
                "is_synced": s.is_synced,
                "casualty_count": len(s.casualties),
            }
            for s in surveys
        ],
    }


@router.get("/stats")
def stats(
    db: Session = Depends(get_db),
    _: str = Depends(require_dev),
):
    total_users = db.scalar(select(func.count()).select_from(User)) or 0
    total_surveys = db.scalar(select(func.count()).select_from(Survey)) or 0
    synced = (
        db.scalar(select(func.count()).select_from(Survey).where(Survey.is_synced.is_(True)))
        or 0
    )
    total_casualties = db.scalar(select(func.count()).select_from(Survey)) or 0
    return {
        "users": total_users,
        "surveys": total_surveys,
        "surveys_synced": synced,
        "casualty_rows": total_casualties,
    }


@router.get("/audit")
def audit(
    limit: int = Query(default=100, le=1000),
    db: Session = Depends(get_db),
    _: str = Depends(require_dev),
):
    exports = db.scalars(
        select(ExportLog).order_by(ExportLog.exported_at.desc()).limit(limit)
    ).all()
    status_changes = db.scalars(
        select(AuditLog).order_by(AuditLog.changed_at.desc()).limit(limit)
    ).all()
    return {
        "exports": [
            {
                "exported_by": e.exported_by,
                "row_count": e.row_count,
                "exported_at": e.exported_at.isoformat() if e.exported_at else None,
            }
            for e in exports
        ],
        "status_changes": [
            {
                "survey_id": str(a.survey_id) if a.survey_id else None,
                "old_status": a.old_status,
                "new_status": a.new_status,
                "changed_at": a.changed_at.isoformat() if a.changed_at else None,
            }
            for a in status_changes
        ],
    }


@router.get("/sync-logs")
def sync_logs(
    limit: int = Query(default=100, le=1000),
    db: Session = Depends(get_db),
    _: str = Depends(require_dev),
):
    rows = db.scalars(
        select(SyncLog).order_by(SyncLog.synced_at.desc()).limit(limit)
    ).all()
    return {
        "count": len(rows),
        "logs": [
            {
                "sync_id": str(r.sync_id),
                "survey_id": str(r.survey_id),
                "sync_status": r.sync_status,
                "synced_at": r.synced_at.isoformat() if r.synced_at else None,
            }
            for r in rows
        ],
    }
