"""
SQLAlchemy models mirroring ../database/schema.sql.
Keep these two files in sync manually for now.
TODO: consider Alembic once the schema stabilizes past this week's prototype.
"""

from sqlalchemy import Column, String, Integer, TIMESTAMP, JSON
from sqlalchemy.orm import declarative_base
from geoalchemy2 import Geometry

Base = declarative_base()


class Device(Base):
    __tablename__ = "devices"
    device_id = Column(String, primary_key=True)
    first_seen_at = Column(TIMESTAMP(timezone=True))
    last_bridge_at = Column(TIMESTAMP(timezone=True))


class Record(Base):
    __tablename__ = "records"
    id = Column(String, primary_key=True)
    device_id = Column(String)
    local_counter = Column(Integer)
    captured_at = Column(TIMESTAMP(timezone=True))
    location = Column(Geometry(geometry_type="POINT", srid=4326))
    survey_data = Column(JSON)
    received_at = Column(TIMESTAMP(timezone=True))
    record_hash = Column(String)
