# here is db/models/attributes/py

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



class YesNoAttributes(Base):
    __tablename__ = 'yes_no_attributes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    attribute_name = Column(String(50), nullable=False)
    attribute_value = Column(Boolean, nullable=False)  # Store True/False values

    user = relationship('User', back_populates='yes_no_attributes')

    def __repr__(self):
        return f"<YesNoAttributes(attribute_name={self.attribute_name}, attribute_value={self.attribute_value})>"

class MultiselectiveAttributes(Base):
    __tablename__ = 'multiselective_attributes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    attribute_name = Column(String(50), nullable=False)
    attribute_value = Column(String(50), nullable=False)  # Store selected option

    user = relationship('User', back_populates='multiselective_attributes')

    def __repr__(self):
        return f"<MultiselectiveAttributes(attribute_name={self.attribute_name}, attribute_value={self.attribute_value})>"

class NumericAttributes(Base):
    __tablename__ = 'numeric_attributes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    attribute_name = Column(String(50), nullable=False)
    attribute_value = Column(Float, nullable=False)  # Store numeric values
    attribute_unit = Column(String(20), nullable=True)  # Store the unit of the attribute, e.g., "kg", "cm"

    user = relationship('User', back_populates='numeric_attributes')

    def __repr__(self):
        return f"<NumericAttributes(attribute_name={self.attribute_name}, attribute_value={self.attribute_value}, attribute_unit={self.attribute_unit})>"

class NumericalScaleAttributes(Base):
    __tablename__ = 'numerical_scale_attributes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    attribute_name = Column(String(50), nullable=False)
    attribute_value = Column(Integer, nullable=False)  # Store scale values, e.g., 1-10

    user = relationship('User', back_populates='numerical_scale_attributes')

    def __repr__(self):
        return f"<NumericalScaleAttributes(attribute_name={self.attribute_name}, attribute_value={self.attribute_value})>"
