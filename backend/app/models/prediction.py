from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float, Text, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class ProjectPrediction(Base):
    __tablename__ = "project_predictions"

    prediction_id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False, index=True)

    model_version = Column(String, nullable=False, default="delay-model-v1")
    feature_schema_version = Column(String, nullable=False, default="v1")

    predicted_probability = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False, default="Low", index=True)
    horizon_days = Column(Integer, nullable=False, default=180)

    top_features_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    data_origin = Column(String, nullable=False, default="synthetic")

    project = relationship("Project")
