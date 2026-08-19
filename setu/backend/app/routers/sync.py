"""Sync endpoints: upload (Phase 3/4) and delta download (Phase 5)."""
from __future__ import annotations

import datetime
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Casualty, DamageImage, ReliefCamp, Survey, SyncLog, User
from ..schemas import (
    CasualtyOut,
    DamageImageOut,
    DownloadResponse,
    ReliefCampOut,
    SurveyOut,
    SurveyIn,
    UploadRequest,
    UploadResponse,
    UploadResult,
    UserOut,
)
from ..security import mask_aadhaar

router = APIRouter(prefix="/api/v1/sync", tags=["sync"])


def _gen_survey_number() -> str:
    year = datetime.date.today().year
    return f"SC-{year}-{uuid.uuid4().hex[:6].upper()}"


def _get_or_create_user(db: Session, s: SurveyIn) -> User:
    existing = db.scalar(
        select(User).where(User.aadhaar_number == s.user.aadhaar_number)
    )
    if existing:
        return existing
    user = User(
        full_name=s.user.full_name,
        father_name=s.user.father_name,
        mobile_number=s.user.mobile_number,
        aadhaar_number=s.user.aadhaar_number,
        family_id=s.user.family_id,
    )
    db.add(user)
    db.flush()
    return user


def _survey_out(s: Survey) -> SurveyOut:
    return SurveyOut(
        survey_id=str(s.survey_id),
        survey_number=s.survey_number,
        village=s.village,
        district=s.district,
        post_office=s.post_office,
        police_station=s.police_station,
        pin_code=s.pin_code,
        disaster_type=s.disaster_type,
        other_disaster_type=s.other_disaster_type,
        damage_date=s.damage_date,
        damage_area=s.damage_area,
        other_damage_area=s.other_damage_area,
        damage_description=s.damage_description,
        survey_status=s.survey_status,
        is_synced=s.is_synced,
        created_at=s.created_at,
        updated_at=s.updated_at,
        user=UserOut(
            full_name=s.user.full_name,
            father_name=s.user.father_name,
            mobile_number=s.user.mobile_number,
            aadhaar_masked=mask_aadhaar(s.user.aadhaar_number),
            family_id=s.user.family_id,
        ),
        casualties=[
            CasualtyOut(
                person_name=c.person_name,
                age=c.age,
                gender=c.gender,
                status=c.status,
                current_location=c.current_location,
            )
            for c in s.casualties
        ],
        relief_camp=(
            ReliefCampOut(
                staying_in_camp=s.relief_camp.staying_in_camp,
                camp_name=s.relief_camp.camp_name,
                camp_location=s.relief_camp.camp_location,
                camp_address=s.relief_camp.camp_address,
                nearest_landmark=s.relief_camp.nearest_landmark,
            )
            if s.relief_camp
            else None
        ),
        damage_images=[DamageImageOut(image_url=i.image_url) for i in s.damage_images],
    )


@router.post("/upload", response_model=UploadResponse)
def upload(payload: UploadRequest, db: Session = Depends(get_db)) -> UploadResponse:
    """Receive a batch of surveys; upsert users, dedupe by (user, damage_date)."""
    accepted = duplicates = rejected = 0
    details: List[UploadResult] = []
    batch_id = f"batch-{uuid.uuid4().hex[:12]}"

    for idx, s in enumerate(payload.surveys):
        user = _get_or_create_user(db, s)
        survey = Survey(
            survey_number=_gen_survey_number(),
            user_id=user.user_id,
            village=s.village,
            district=s.district,
            post_office=s.post_office,
            police_station=s.police_station,
            pin_code=s.pin_code,
            disaster_type=s.disaster_type,
            other_disaster_type=s.other_disaster_type,
            damage_date=s.damage_date,
            damage_area=s.damage_area,
            other_damage_area=s.other_damage_area,
            damage_description=s.damage_description,
            survey_status="synced",
            is_synced=True,
        )
        try:
            db.add(survey)
            db.flush()  # raises IntegrityError on duplicate (user_id, damage_date)
            for c in s.casualties:
                db.add(
                    Casualty(
                        survey_id=survey.survey_id,
                        person_name=c.person_name,
                        age=c.age,
                        gender=c.gender,
                        status=c.status,
                        current_location=c.current_location,
                    )
                )
            if s.relief_camp:
                rc = s.relief_camp
                db.add(
                    ReliefCamp(
                        survey_id=survey.survey_id,
                        staying_in_camp=rc.staying_in_camp,
                        camp_name=rc.camp_name,
                        camp_location=rc.camp_location,
                        camp_address=rc.camp_address,
                        nearest_landmark=rc.nearest_landmark,
                    )
                )
            for img in s.images:
                db.add(DamageImage(survey_id=survey.survey_id, image_url=img.image_url))
            db.add(SyncLog(survey_id=survey.survey_id, sync_status="synced"))
            db.commit()
            accepted += 1
            details.append(
                UploadResult(survey_number=survey.survey_number, outcome="accepted")
            )
        except IntegrityError:
            db.rollback()
            duplicates += 1
            details.append(
                UploadResult(
                    outcome="duplicate",
                    reason="survey already exists for this Aadhaar on this damage date",
                )
            )
        except Exception as exc:  # pragma: no cover - defensive
            db.rollback()
            rejected += 1
            details.append(
                UploadResult(outcome="rejected", reason=f"survey[{idx}]: {exc}")
            )

    return UploadResponse(
        batchId=batch_id,
        accepted=accepted,
        duplicates=duplicates,
        rejected=rejected,
        rejectedDetails=details,
    )


@router.get("/download", response_model=DownloadResponse)
def download(
    since: Optional[str] = Query(
        default=None, description="ISO-8601 UTC cursor, e.g. 2026-08-15T10:30:00Z"
    ),
    db: Session = Depends(get_db),
) -> DownloadResponse:
    """Return surveys changed after `since` (or all). `nextCursor` enables delta pulls."""
    cursor: Optional[datetime.datetime] = None
    if since:
        try:
            cursor = datetime.datetime.fromisoformat(since.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "invalid_cursor",
                        "message": "since must be an ISO-8601 UTC timestamp",
                    }
                },
            )

    stmt = select(Survey).join(User)
    if cursor:
        stmt = stmt.where(Survey.updated_at > cursor)
    stmt = stmt.order_by(Survey.updated_at.asc())
    surveys = db.scalars(stmt).all()

    out = [_survey_out(s) for s in surveys]
    next_cursor = out[-1].updated_at.isoformat() if out else None
    return DownloadResponse(since=since, surveys=out, nextCursor=next_cursor)
