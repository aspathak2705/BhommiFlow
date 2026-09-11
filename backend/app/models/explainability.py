from sqlalchemy import Column, String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class ProjectExplanation(Base):
    __tablename__ = "project_explanations"

    explanation_id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False, index=True)
    prediction_id = Column(String, ForeignKey("project_predictions.prediction_id", ondelete="SET NULL"), nullable=True)

    explanation_version = Column(String, nullable=False, default="v1")
    summary = Column(Text, nullable=False)
    explanation_json = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    data_origin = Column(String, nullable=False, default="synthetic")

    project = relationship("Project")
    prediction = relationship("ProjectPrediction")


class InterventionCandidate(Base):
    __tablename__ = "intervention_candidates"

    intervention_id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False, index=True)
    bottleneck_id = Column(String, ForeignKey("bottleneck_signals.bottleneck_id", ondelete="SET NULL"), nullable=True)

    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    target_bottleneck = Column(String, nullable=False)
    priority = Column(String, nullable=False, default="Medium")
    expected_process_effect = Column(Text, nullable=False)
    required_evidence = Column(Text, nullable=True)
    rule_id = Column(String, nullable=True)
    status = Column(String, nullable=False, default="Recommended")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    data_origin = Column(String, nullable=False, default="synthetic")

    project = relationship("Project")
    bottleneck = relationship("BottleneckSignal")
