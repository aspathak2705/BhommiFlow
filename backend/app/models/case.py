from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Case(Base):
    __tablename__ = "cases"

    case_id = Column(String, primary_key=True, index=True)
    case_reference = Column(String, unique=True, index=True, nullable=False)
    citizen_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    case_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(String, nullable=False, default="DRAFT")  # DRAFT, SUBMITTED, UNDER_REVIEW, ACTION_REQUIRED, CLOSED
    priority = Column(String, nullable=False, default="MEDIUM")
    district = Column(String, nullable=False)
    taluka = Column(String, nullable=False)
    village = Column(String, nullable=False)
    assigned_officer_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    citizen = relationship("User", foreign_keys=[citizen_id])
    assigned_officer = relationship("User", foreign_keys=[assigned_officer_id])
    land_parcels = relationship("LandParcel", back_populates="case", cascade="all, delete-orphan")
    people = relationship("CasePerson", back_populates="case", cascade="all, delete-orphan")
    events = relationship("CaseEvent", back_populates="case", cascade="all, delete-orphan")

class LandParcel(Base):
    __tablename__ = "land_parcels"

    id = Column(String, primary_key=True, index=True)
    case_id = Column(String, ForeignKey("cases.case_id", ondelete="CASCADE"), nullable=False)
    district = Column(String, nullable=False)
    taluka = Column(String, nullable=False)
    village = Column(String, nullable=False)
    survey_number = Column(String, nullable=True)
    subdivision_number = Column(String, nullable=True)
    property_type = Column(String, nullable=True)
    area = Column(Float, nullable=True)
    area_unit = Column(String, nullable=True)
    description = Column(String, nullable=True)

    case = relationship("Case", back_populates="land_parcels")

class Person(Base):
    __tablename__ = "persons"

    id = Column(String, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    address = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CasePerson(Base):
    __tablename__ = "case_persons"

    id = Column(String, primary_key=True, index=True)
    case_id = Column(String, ForeignKey("cases.case_id", ondelete="CASCADE"), nullable=False)
    person_id = Column(String, ForeignKey("persons.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False)  # owner, heir, buyer, seller, applicant, other
    notes = Column(String, nullable=True)

    case = relationship("Case", back_populates="people")
    person = relationship("Person")

class CaseEvent(Base):
    __tablename__ = "case_events"

    event_id = Column(String, primary_key=True, index=True)
    case_id = Column(String, ForeignKey("cases.case_id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String, nullable=False)  # CASE_CREATED, CASE_SUBMITTED, STATUS_CHANGED, NOTE_ADDED
    actor_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    actor_role = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    metadata_json = Column(String, nullable=True)  # Simple metadata storage

    case = relationship("Case", back_populates="events")
    actor = relationship("User")
