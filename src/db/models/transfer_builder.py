"""
transfer_builder.py

SQLAlchemy model definition for the 'transferbuilder' table.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Boolean,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TransferBuilder(Base):
    __tablename__ = "transferbuilder"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    request_id = Column(String(255), nullable=False)

    # Time columns
    be_incall_time = Column(DateTime, nullable=True)
    fe_incall_time = Column(DateTime, nullable=True)

    # Buy-related columns
    requested_buy_amount_in_pepe = Column(Float, nullable=False)
    prefered_payment_asset = Column(String(50), nullable=True)
    how_much_should_be_paid = Column(Float, nullable=False)

    # Info columns
    email = Column(String(255), nullable=True)
    telegram = Column(String(255), nullable=True)

    # Price / snapshot columns
    pepe_price_in_usdt = Column(Float, nullable=True)
    pepe_price_snapshot_time = Column(DateTime, nullable=True)

    # Timeout
    timeout_time = Column(DateTime, nullable=True)

    # USDT deposit address generation
    generated_usdt_address = Column(String(255), nullable=True)
    generated_usdt_address_fe_incall_time = Column(DateTime, nullable=True)

    # Payment confirmation
    payment_done_clicked = Column(Boolean, default=False)
    payment_done_clicked_fe_time = Column(DateTime, nullable=True)

    def __init__(
        self,
        user_id,
        request_id,
        be_incall_time,
        fe_incall_time,
        requested_buy_amount_in_pepe,
        prefered_payment_asset,
        how_much_should_be_paid,
        email,
        pepe_price_in_usdt,
        pepe_price_snapshot_time,
        telegram,
        timeout_time,
        generated_usdt_address,
        generated_usdt_address_fe_incall_time,
        payment_done_clicked,
        payment_done_clicked_fe_time
    ):
        self.user_id = user_id
        self.request_id = request_id
        self.be_incall_time = be_incall_time
        self.fe_incall_time = fe_incall_time
        self.requested_buy_amount_in_pepe = requested_buy_amount_in_pepe
        self.prefered_payment_asset = prefered_payment_asset
        self.how_much_should_be_paid = how_much_should_be_paid
        self.email = email
        self.pepe_price_in_usdt = pepe_price_in_usdt
        self.pepe_price_snapshot_time = pepe_price_snapshot_time
        self.telegram = telegram
        self.timeout_time = timeout_time
        self.generated_usdt_address = generated_usdt_address
        self.generated_usdt_address_fe_incall_time = generated_usdt_address_fe_incall_time
        self.payment_done_clicked = payment_done_clicked
        self.payment_done_clicked_fe_time = payment_done_clicked_fe_time
