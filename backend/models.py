from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from database import Base


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    github_url = Column(String(500), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    local_path = Column(String(500), nullable=False)
    branch = Column(String(100))
    language = Column(String(100))
    stars = Column(Integer, default=0)
    forks = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    analyses = relationship(
        "Analysis",
        back_populates="repository",
        cascade="all, delete-orphan"
    )


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)

    repository_id = Column(
        Integer,
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
    )

    overall_risk = Column(Float)
    average_complexity = Column(Float)
    maintainability_index = Column(Float)

    architecture_score = Column(Float)

    code_health = Column(Float)

    overall_grade = Column(String(5))

    risk_level = Column(String(30))

    dependency_graph = Column(Text)
    git_summary = Column(Text)
    report = Column(Text)

    analyzed_at = Column(DateTime, default=datetime.utcnow)

    repository = relationship("Repository", back_populates="analyses")

    files = relationship(
        "FileMetric",
        back_populates="analysis",
        cascade="all, delete-orphan"
    )


class FileMetric(Base):
    __tablename__ = "file_metrics"

    id = Column(Integer, primary_key=True, index=True)

    analysis_id = Column(
        Integer,
        ForeignKey("analyses.id", ondelete="CASCADE"),
        nullable=False,
    )

    file_path = Column(String(500), nullable=False)

    language = Column(String(50))

    lines = Column(Integer)

    cyclomatic_complexity = Column(Float)

    maintainability_index = Column(Float)

    risk_score = Column(Float)

    duplicate_percentage = Column(Float)

    git_churn = Column(Integer)

    dead_code = Column(Text)

    hotspot_score = Column(Float)

    analysis = relationship("Analysis", back_populates="files")