from sqlalchemy import Column, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class PotentialConflict(Base):
    __tablename__ = "potential_conflicts"

    conflict_id = Column(String, primary_key=True, index=True)
    case_id = Column(String, ForeignKey("cases.case_id", ondelete="CASCADE"), nullable=False)
    conflict_type = Column(String, nullable=False)  # NAME_VARIATION, DATE_DISCREPANCY, SURVEY_MISMATCH, etc.
    severity = Column(String, nullable=False, default="REVIEW_REQUIRED")  # INFO, REVIEW_REQUIRED
    description = Column(String, nullable=False)
    status = Column(String, nullable=False, default="OPEN")  # OPEN, REVIEWED, DISMISSED
    source_entity_a = Column(String, nullable=True)  # Reference to first source
    source_entity_b = Column(String, nullable=True)  # Reference to second source
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    reviewed_by = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    case = relationship("Case")
    reviewer = relationship("User")
