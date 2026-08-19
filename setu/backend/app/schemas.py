"""Pydantic request/response models for the API.

These mirror the teammate's DB schema (users/surveys/casualties/relief_camps/
damage_images). Validation rules replicate the DB CHECK constraints so malformed
batches are rejected with clean 400s before they reach the database.
"""
from __future__ import annotations

import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

MOBILE_RE = r"^\d{10}$"
AADHAAR_RE = r"^\d{12}$"
PIN_RE = r"^\d{6}$"

GENDERS = {"Male", "Female", "Other"}
STATUSES = {"Alive", "Missing", "Not Alive"}


class UserIn(BaseModel):
    full_name: str = Field(min_length=1, max_length=100)
    father_name: str = Field(min_length=1, max_length=100)
    mobile_number: str = Field(pattern=MOBILE_RE)
    aadhaar_number: str = Field(pattern=AADHAAR_RE)
    family_id: Optional[str] = Field(default=None, max_length=20)


class CasualtyIn(BaseModel):
    person_name: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=0, le=120)
    gender: str
    status: str
    current_location: str = Field(min_length=1)

    @field_validator("gender")
    @classmethod
    def _gender(cls, v: str) -> str:
        if v not in GENDERS:
            raise ValueError(f"gender must be one of {sorted(GENDERS)}")
        return v

    @field_validator("status")
    @classmethod
    def _status(cls, v: str) -> str:
        if v not in STATUSES:
            raise ValueError(f"status must be one of {sorted(STATUSES)}")
        return v


class ReliefCampIn(BaseModel):
    staying_in_camp: bool = False
    camp_name: Optional[str] = Field(default=None, max_length=100)
    camp_location: Optional[str] = Field(default=None, max_length=100)
    camp_address: Optional[str] = None
    nearest_landmark: Optional[str] = Field(default=None, max_length=200)


class DamageImageIn(BaseModel):
    image_url: str = Field(min_length=1)


class SurveyIn(BaseModel):
    user: UserIn
    village: str = Field(min_length=1, max_length=100)
    district: str = Field(min_length=1, max_length=100)
    post_office: str = Field(min_length=1, max_length=100)
    police_station: str = Field(min_length=1, max_length=100)
    pin_code: str = Field(pattern=PIN_RE)
    disaster_type: str = Field(min_length=1, max_length=50)
    other_disaster_type: Optional[str] = Field(default=None, max_length=100)
    damage_date: datetime.date
    damage_area: str = Field(min_length=1)
    other_damage_area: Optional[str] = Field(default=None, max_length=100)
    damage_description: Optional[str] = None
    casualties: List[CasualtyIn] = Field(default_factory=list)
    relief_camp: Optional[ReliefCampIn] = None
    images: List[DamageImageIn] = Field(default_factory=list)


class UploadRequest(BaseModel):
    surveys: List[SurveyIn] = Field(min_length=1)


# ----------------------------- Responses -----------------------------


class UserOut(BaseModel):
    full_name: str
    father_name: str
    mobile_number: str
    aadhaar_masked: str
    family_id: Optional[str] = None


class CasualtyOut(BaseModel):
    person_name: str
    age: int
    gender: str
    status: str
    current_location: str


class ReliefCampOut(BaseModel):
    staying_in_camp: bool
    camp_name: Optional[str] = None
    camp_location: Optional[str] = None
    camp_address: Optional[str] = None
    nearest_landmark: Optional[str] = None


class DamageImageOut(BaseModel):
    image_url: str


class SurveyOut(BaseModel):
    survey_id: str
    survey_number: Optional[str] = None
    village: str
    district: str
    post_office: str
    police_station: str
    pin_code: str
    disaster_type: str
    other_disaster_type: Optional[str] = None
    damage_date: datetime.date
    damage_area: str
    other_damage_area: Optional[str] = None
    damage_description: Optional[str] = None
    survey_status: str
    is_synced: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime
    user: UserOut
    casualties: List[CasualtyOut] = Field(default_factory=list)
    relief_camp: Optional[ReliefCampOut] = None
    damage_images: List[DamageImageOut] = Field(default_factory=list)


class UploadResult(BaseModel):
    survey_number: Optional[str] = None
    outcome: str  # accepted | duplicate | rejected
    reason: Optional[str] = None


class UploadResponse(BaseModel):
    batchId: str
    accepted: int
    duplicates: int
    rejected: int
    rejectedDetails: List[UploadResult] = Field(default_factory=list)


class DownloadResponse(BaseModel):
    since: Optional[str] = None
    surveys: List[SurveyOut] = Field(default_factory=list)
    nextCursor: Optional[str] = None


class LoginRequest(BaseModel):
    api_key: str


class TokenResponse(BaseModel):
    token: str
    expiresIn: int
    role: str
