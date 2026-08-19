"""SQLAlchemy ORM models — mirror the teammate's PostgreSQL schema (setu_postgresql.sql).

The cloud DB (Neon Postgres) is the source of truth; the same models run against
SQLite for local dev/test. PKs use the dialect-agnostic ``Uuid`` type so a single
model works on both databases.

Tables: users, surveys, damage_images, casualties, relief_camps, sync_logs,
audit_logs, plus ExportLog (added for export auditing, which the original schema
lacked).
"""

from __future__ import annotations

import datetime
import uuid
from typing import Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)

from .db import Base


def _utcnow() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    father_name: Mapped[str] = mapped_column(String(100), nullable=False)
    mobile_number: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    aadhaar_number: Mapped[str] = mapped_column(String(12), nullable=False, unique=True)
    family_id: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=_utcnow
    )

    surveys: Mapped[list["Survey"]] = relationship(back_populates="user")


class Survey(Base):
    __tablename__ = "surveys"

    survey_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    survey_number: Mapped[Optional[str]] = mapped_column(String(20), unique=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.user_id"), nullable=False
    )
    village: Mapped[str] = mapped_column(String(100), nullable=False)
    district: Mapped[str] = mapped_column(String(100), nullable=False)
    post_office: Mapped[str] = mapped_column(String(100), nullable=False)
    police_station: Mapped[str] = mapped_column(String(100), nullable=False)
    pin_code: Mapped[str] = mapped_column(String(6), nullable=False)
    disaster_type: Mapped[str] = mapped_column(String(50), nullable=False)
    other_disaster_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    damage_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    damage_area: Mapped[str] = mapped_column(Text, nullable=False)
    other_damage_area: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    damage_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    survey_status: Mapped[str] = mapped_column(String(20), default="offline")
    is_synced: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=_utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=_utcnow, onupdate=_utcnow
    )

    user: Mapped["User"] = relationship(back_populates="surveys")
    casualties: Mapped[list["Casualty"]] = relationship(
        back_populates="survey", cascade="all, delete-orphan"
    )
    relief_camp: Mapped[Optional["ReliefCamp"]] = relationship(
        back_populates="survey", cascade="all, delete-orphan", uselist=False
    )
    damage_images: Mapped[list["DamageImage"]] = relationship(
        back_populates="survey", cascade="all, delete-orphan"
    )
    sync_logs: Mapped[list["SyncLog"]] = relationship(
        back_populates="survey", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("user_id", "damage_date", name="uq_user_damage_date"),
    )


class DamageImage(Base):
    __tablename__ = "damage_images"

    image_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    survey_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("surveys.survey_id"), nullable=False
    )
    image_url: Mapped[str] = mapped_column(Text, nullable=False)
    uploaded_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=_utcnow)

    survey: Mapped["Survey"] = relationship(back_populates="damage_images")


class Casualty(Base):
    __tablename__ = "casualties"

    casualty_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    survey_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("surveys.survey_id"), nullable=False
    )
    person_name: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[int] = mapped_column(nullable=False)
    gender: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    current_location: Mapped[str] = mapped_column(Text, nullable=False)

    survey: Mapped["Survey"] = relationship(back_populates="casualties")


class ReliefCamp(Base):
    __tablename__ = "relief_camps"

    camp_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    survey_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("surveys.survey_id"), nullable=False
    )
    staying_in_camp: Mapped[bool] = mapped_column(Boolean, default=False)
    camp_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    camp_location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    camp_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    nearest_landmark: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    survey: Mapped["Survey"] = relationship(back_populates="relief_camp")


class SyncLog(Base):
    __tablename__ = "sync_logs"

    sync_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    survey_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("surveys.survey_id"), nullable=False
    )
    sync_status: Mapped[str] = mapped_column(String(20), default="pending")
    synced_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=_utcnow)

    survey: Mapped["Survey"] = relationship(back_populates="sync_logs")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    log_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    survey_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True)
    old_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    new_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    changed_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=_utcnow)


class ExportLog(Base):
    """Export auditing — added because the original audit_logs only tracks status changes."""

    __tablename__ = "export_logs"

    export_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    exported_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    row_count: Mapped[int] = mapped_column(default=0)
    exported_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=_utcnow)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
