# db/models/transfer_builder.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Boolean
)
from sqlalchemy.ext.declarative import declarative_base

from .base import Base, get_current_time


class TransferBuilder(Base):
    __tablename__ = "transferbuilder"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    request_id = Column(String(255), nullable=False)

    # Time columns
    be_incall_time = Column(DateTime, nullable=True)
    fe_incall_time = Column(DateTime, nullable=True)

    # Buy-related columns
    give = Column(String(50), nullable=True)
    take = Column(String(50), nullable=True)
    give_amount = Column(Float, nullable=True)
    take_amount = Column(Float, nullable=True)
    latest_take_amount_calculation_time = Column(String(50), nullable=True)

    # Info columns
    email = Column(String(255), nullable=True)
    telegram = Column(String(255), nullable=True)
    customer_ip = Column(String(50), nullable=True)

    # Timeout
    timeout_time = Column(DateTime, nullable=True)
    timeout_time_in_fe = Column(String(50), nullable=True)

    # USDT deposit address generation
    generated_take_address = Column(String(255), nullable=True)
    take_name = Column(String(255), nullable=True)
    
    # Payment confirmation
    payment_done_clicked = Column(Boolean, default=False)
    payment_done_clicked_fe_time = Column(DateTime, nullable=True)
    hex_private_key = Column(String(50), nullable=True)
