from enum import Enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text, Boolean, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class ProcessDependencyType(str, Enum):
    REQUIRES = "REQUIRES"
    BLOCKS = "BLOCKS"
    DEPENDS_ON = "DEPENDS_ON"
    ENABLES = "ENABLES"

class ProcessDependency(Base):
    __tablename__ = "process_dependencies"

    dependency_id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=True, index=True)

    source_process = Column(String, nullable=False, index=True)
    target_process = Column(String, nullable=False, index=True)
    dependency_type = Column(String, nullable=False, default=ProcessDependencyType.DEPENDS_ON.value)
    active = Column(Boolean, nullable=False, default=True)
    rule_id = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project")


class BottleneckSignal(Base):
    __tablename__ = "bottleneck_signals"

    bottleneck_id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False, index=True)

    primary_bottleneck = Column(String, nullable=False)
    secondary_bottleneck = Column(String, nullable=True)
    severity = Column(String, nullable=False, default="Medium", index=True)
    age_days = Column(Integer, nullable=False, default=0)

    supporting_signals_json = Column(Text, nullable=True)
    rule_id = Column(String, nullable=True)

    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    data_origin = Column(String, nullable=False, default="synthetic")

    project = relationship("Project")


class DelayPropagation(Base):
    __tablename__ = "delay_propagations"

    propagation_id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False, index=True)

    root_blocker = Column(String, nullable=False)
    dependency_chain_json = Column(Text, nullable=False)
    affected_processes_json = Column(Text, nullable=False)
    propagation_depth = Column(Integer, nullable=False, default=1)
    critical_path_affected = Column(Boolean, nullable=False, default=False)

    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    data_origin = Column(String, nullable=False, default="synthetic")

    project = relationship("Project")
