# here is db/models/user.py

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


class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=get_current_time)
    is_verified = Column(Boolean, default=False)
    family_mode = Column(Boolean, default=False, nullable=False)
    

   
    def __repr__(self):
        return f"<User(name={self.name}, email={self.email})>"


# class UserFeatureUsage(Base):
#     __tablename__ = 'user_feature_usage'
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False, unique=True)
#     pdfs_uploaded_this_month = Column(Integer, nullable=False, default=0)
#     bank_accounts_added = Column(Integer, nullable=False, default=0)
#     family_members_added = Column(Integer, nullable=False, default=0)
#     splits_made_this_month = Column(Integer, nullable=False, default=0)
#     last_reset_date = Column(DateTime, nullable=False, default=get_current_time)

#     # Relationships
#     user = relationship('User', back_populates='feature_usage')

#     def __repr__(self):
#         return f"<UserFeatureUsage(user_id={self.user_id})>"


