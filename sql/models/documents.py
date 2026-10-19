from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from db import Base



# SQLAlchemy ORM model for tracked document uploads.
# Stores both original filename and the renamed path used after vector ingestion.
class Document(Base):
    """
    Tracks uploaded documents and web scrapes.
    
    Fields:
        employee_id: uploader's employee ID.
        original_path: human-facing filename at time of upload.
        doc_path: internal path on disk under 'documents/' (renamed with '_' prefix
                  after the background scheduler successfully splits & embeds it).
        type: visibility scope ('public' or 'private').
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    original_path = Column(String(255), nullable=False)
    doc_path = Column(String(255), nullable=False)
    type = Column(String(50), unique=True, index=True, nullable=False)
    employee = relationship("Employee")
    created_at = Column(DateTime, default=datetime.now, nullable=False)


