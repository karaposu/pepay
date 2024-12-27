from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, DateTime, Text, Enum
)
from sqlalchemy.types import JSON
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class LogLevelEnum(enum.Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogRecord(Base):
    __tablename__ = 'log_records'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    level = Column(Enum(LogLevelEnum), nullable=False)  # uses enum for controlled values
    message = Column(Text, nullable=False)
    request_id = Column(String(50), nullable=True, index=True)  # index for quick filtering by request
    user_id = Column(Integer, nullable=True, index=True)
    operation = Column(String(100), nullable=True, index=True)  
    endpoint = Column(String(200), nullable=True, index=True)
    method = Column(String(10), nullable=True)
    extra = Column(JSON, nullable=True)  # Storing additional structured data (if supported by your DB)
    
    def __repr__(self):
        return f"<LogRecord(id={self.id}, level={self.level}, message={self.message[:50]}...)>"
