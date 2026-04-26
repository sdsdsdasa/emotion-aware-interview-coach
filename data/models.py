from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from .db import Base

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String, index=True)          # uuid you generate
    input_filename = Column(String)
    status = Column(String, default="completed")
    timeline_json = Column(Text)                   # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
