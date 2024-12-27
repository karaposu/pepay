# here is db/models/bank_account.py

from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, Float, Text,
    ForeignKey, LargeBinary, Boolean, UniqueConstraint, CheckConstraint, or_, func
)
from sqlalchemy.types import JSON
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash

from .base import Base


class BankAccount(Base):
    __tablename__ = 'bank_accounts'

    bank_account_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    bank_name = Column(String(100), nullable=False)
    bank_account_id_alias = Column(String(100), nullable=True)
    currency = Column(String(10), nullable=False)
    bank_account_number = Column(String(50), nullable=True)
    bank_account_name = Column(String(100), nullable=True)
    iban = Column(String(50), nullable=True)
    other_details = Column(Text, nullable=True)

    # Relationships
    user = relationship('User', back_populates='bank_accounts')
    initial_data = relationship('InitialData', back_populates='bank_account', cascade='all, delete-orphan')
    processed_data = relationship('ProcessedData', back_populates='bank_account', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<BankAccount(bank_name={self.bank_name}, bank_account_name={self.bank_account_name})>"
