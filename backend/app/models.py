from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Results(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, index=True)
    transcription = Column(String)
    confidence_score = Column(String)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
