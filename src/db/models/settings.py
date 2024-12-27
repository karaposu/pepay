# here is db/models/settings.py


from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, Float, Text,
    ForeignKey, LargeBinary, Boolean, UniqueConstraint, CheckConstraint, or_, func
)
from sqlalchemy.types import JSON
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash

from .base import Base, get_current_time


class UserSettings(Base):
    __tablename__ = 'user_settings'
    setting_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    piechart_settings = Column(JSON, nullable=True)
    notification_preferences = Column(JSON, nullable=True)
    theme_preferences = Column(JSON, nullable=True)
    default_currency = Column(String, nullable=True)  # ISO currency codes are usually 3 characters
    default_country = Column(String, nullable=True)  # ISO currency codes are usually 3 characters
    default_bank = Column(String, nullable=True)  # ISO currency codes are usually 3 characters



    user = relationship("User", back_populates="settings")