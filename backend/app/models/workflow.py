from sqlalchemy import Column, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class EvidenceRequest(Base):
    __tablename__ = "evidence_requests"

    request_id = Column(String, primary_key=True, index=True)
    case_id = Column(String, ForeignKey("cases.case_id", ondelete="CASCADE"), nullable=False)
    requested_by = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    description = Column(String, nullable=False)
    status = Column(String, nullable=False, default="OPEN")  # OPEN, FULFILLED, CANCELLED
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    fulfilled_at = Column(DateTime(timezone=True), nullable=True)

    case = relationship("Case")
    requester = relationship("User")

class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    case_id = Column(String, ForeignKey("cases.case_id", ondelete="CASCADE"), nullable=False)
    channel = Column(String, nullable=False, default="SMS")  # SMS, EMAIL, etc.
    event_type = Column(String, nullable=False)  # CASE_SUBMITTED, CASE_STATUS_CHANGED, etc.
    message = Column(String, nullable=False)
    status = Column(String, nullable=False, default="PENDING")  # PENDING, SENT, FAILED
    provider_reference = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sent_at = Column(DateTime(timezone=True), nullable=True)

    case = relationship("Case")
    user = relationship("User")
