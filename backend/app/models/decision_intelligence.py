from sqlalchemy import Column, String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class OfficerDecision(Base):
    __tablename__ = "officer_decisions"

    decision_id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False, index=True)
    prediction_id = Column(String, ForeignKey("project_predictions.prediction_id", ondelete="SET NULL"), nullable=True)
    intervention_id = Column(String, ForeignKey("intervention_candidates.intervention_id", ondelete="SET NULL"), nullable=True)
    officer_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    decision_type = Column(String, nullable=False, default="REVIEW")
    decision_status = Column(String, nullable=False, default="RECOMMENDED")
    decision_reason = Column(Text, nullable=True)
    selected_action = Column(String, nullable=True)

    decision_context_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    data_origin = Column(String, nullable=False, default="synthetic")

    project = relationship("Project")
    prediction = relationship("ProjectPrediction")
    intervention = relationship("InterventionCandidate")
    officer = relationship("User")


class OfficerAction(Base):
    __tablename__ = "officer_actions"

    action_id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False, index=True)
    decision_id = Column(String, ForeignKey("officer_decisions.decision_id", ondelete="SET NULL"), nullable=True, index=True)
    officer_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    action_type = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    target_entity = Column(String, nullable=True)
    status = Column(String, nullable=False, default="INITIATED")
    outcome_status = Column(String, nullable=True)
    outcome_note = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    data_origin = Column(String, nullable=False, default="synthetic")

    project = relationship("Project")
    decision = relationship("OfficerDecision")
    officer = relationship("User")


class DecisionAuditEvent(Base):
    __tablename__ = "decision_audit_events"

    event_id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False, index=True)
    actor_id = Column(String, nullable=False)
    actor_type = Column(String, nullable=False, default="OFFICER")
    event_type = Column(String, nullable=False)
    target_entity = Column(String, nullable=True)
    event_metadata_json = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    data_origin = Column(String, nullable=False, default="synthetic")

    project = relationship("Project")
