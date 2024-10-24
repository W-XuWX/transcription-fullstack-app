from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Results(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, index=True)
    transcription = Column(String)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    # Add an index for faster text search
    __table_args__ = (
        Index('idx_transcription_text', 'transcription'),
    )    

class ResultsSearch(Base):
    """Virtual table for Full Text Search - Schema Only
    Actual table creation is handled in DBClient.init_fts()
    """
    __tablename__ = 'results_search'
    
    id = Column(Integer, primary_key=True)
    file_name = Column(String)
    transcription = Column(String)
    
    # Prevent SQLAlchemy from trying to create this table
    __table_args__ = {'extend_existing': True}