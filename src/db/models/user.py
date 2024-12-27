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
    plan_id = Column(Integer, ForeignKey('plans.plan_id'), nullable=False,  default=1 )


    # Relationships
    feature_usage = relationship('UserFeatureUsage', back_populates='user', uselist=False, cascade='all, delete-orphan')

    bank_accounts = relationship('BankAccount', back_populates='user', cascade='all, delete-orphan')

    plan = relationship('Plan', back_populates='users')
    created_family_groups = relationship('FamilyGroup', back_populates='created_by_user')
    family_memberships = relationship('UserFamilyGroup', back_populates='user', cascade='all, delete-orphan')
    family_members = relationship('FamilyMember', back_populates='parent_user', cascade='all, delete-orphan')
    uploads = relationship("InitialData", back_populates="user", foreign_keys="InitialData.user_id")
    processed_data = relationship("ProcessedData", back_populates="user", foreign_keys="ProcessedData.user_id")
    monthly_aggregations = relationship("MonthlyAggregations", order_by='MonthlyAggregations.agg_id', back_populates="user")
    settings = relationship("UserSettings", order_by='UserSettings.setting_id', back_populates="user")

    # Relationships to different attribute tables
    yes_no_attributes = relationship('YesNoAttributes', back_populates='user', cascade="all, delete-orphan")
    multiselective_attributes = relationship('MultiselectiveAttributes', back_populates='user', cascade="all, delete-orphan")
    numeric_attributes = relationship('NumericAttributes', back_populates='user', cascade="all, delete-orphan")
    numerical_scale_attributes = relationship('NumericalScaleAttributes', back_populates='user', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(name={self.name}, email={self.email})>"


class UserFeatureUsage(Base):
    __tablename__ = 'user_feature_usage'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False, unique=True)
    pdfs_uploaded_this_month = Column(Integer, nullable=False, default=0)
    bank_accounts_added = Column(Integer, nullable=False, default=0)
    family_members_added = Column(Integer, nullable=False, default=0)
    splits_made_this_month = Column(Integer, nullable=False, default=0)
    last_reset_date = Column(DateTime, nullable=False, default=get_current_time)

    # Relationships
    user = relationship('User', back_populates='feature_usage')

    def __repr__(self):
        return f"<UserFeatureUsage(user_id={self.user_id})>"


class Plan(Base):
    __tablename__ = 'plans'
    plan_id = Column(Integer, primary_key=True, autoincrement=True)
    plan_name = Column(String(50), nullable=False, unique=True)
    max_pdfs_per_month = Column(Integer, nullable=False, default=10)
    max_bank_accounts = Column(Integer, nullable=False, default=5)
    max_family_members = Column(Integer, nullable=False, default=3)
    max_record_text_length = Column(Integer, nullable=False, default=500)
    max_splits_per_record = Column(Integer, nullable=False, default=5)

    # Relationships
    users = relationship('User', back_populates='plan')

    def __repr__(self):
        return f"<Plan(plan_name={self.plan_name})>"