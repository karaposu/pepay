# here is db/models/family.py

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



class FamilyGroup(Base):
    __tablename__ = 'family_groups'
    family_group_id = Column(Integer, primary_key=True, autoincrement=True)
    family_group_oid = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    family_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=get_current_time)
    created_by_user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)

    # Relationships
    created_by_user = relationship('User', back_populates='created_family_groups')
    user_memberships = relationship('UserFamilyGroup', back_populates='family_group', cascade='all, delete-orphan')
    family_members = relationship('FamilyMember', back_populates='family_group', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<FamilyGroup(family_name={self.family_name})>"

class UserFamilyGroup(Base):
    __tablename__ = 'user_family_group'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    family_group_id = Column(Integer, ForeignKey('family_groups.family_group_id'), nullable=False)
    joined_at = Column(DateTime, default=get_current_time)

    # Privacy settings per user per family group
    hide_transactions = Column(Boolean, default=False, nullable=False)
    anonymize_records = Column(Boolean, default=False, nullable=False)

    # Relationships
    user = relationship('User', back_populates='family_memberships')
    family_group = relationship('FamilyGroup', back_populates='user_memberships')

    __table_args__ = (UniqueConstraint('user_id', 'family_group_id', name='_user_family_uc'),)

    def __repr__(self):
        return f"<UserFamilyGroup(user_id={self.user_id}, family_group_id={self.family_group_id})>"

class FamilyMember(Base):
    __tablename__ = 'family_members'
    family_member_id = Column(Integer, primary_key=True, autoincrement=True)
    family_member_oid = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    parent_user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    family_group_id = Column(Integer, ForeignKey('family_groups.family_group_id'), nullable=False)
    name = Column(String(50), nullable=False)
    member_relationship = Column(String(50), nullable=True)  # e.g., 'Spouse', 'Child'
    created_at = Column(DateTime, default=get_current_time)

    separate_login = Column(Boolean, default=False, nullable=False)
    email = Column(String(100), unique=True, nullable=True)  # Only if separate_login is True

    # Privacy settings
    hide_transactions = Column(Boolean, default=False, nullable=False)
    anonymize_records = Column(Boolean, default=False, nullable=False)

    # Relationships
    parent_user = relationship('User', back_populates='family_members')
    family_group = relationship('FamilyGroup', back_populates='family_members')
    initial_data = relationship(
        'InitialData',
        back_populates='family_member',
        cascade="all, delete-orphan",
        foreign_keys="InitialData.family_member_id"
    )
    processed_data = relationship(
        'ProcessedData',
        back_populates='family_member',
        cascade="all, delete-orphan",
        foreign_keys="ProcessedData.family_member_id"
    )

    def __repr__(self):
        return f"<FamilyMember(name={self.name}, relationship={self.member_relationship})>"
