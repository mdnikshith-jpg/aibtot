from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String, nullable=True)
    google_id = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# ... existing User model ...

class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    original_filename = Column(String)
    saved_filename = Column(String, unique=True)
    semester = Column(String)
    subject = Column(String)
    module = Column(String, nullable=True)
    file_url = Column(String)   # <--- CHANGED from file_path
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    upload_date = Column(DateTime, default=datetime.utcnow)
    file_size = Column(Integer)
    mime_type = Column(String)