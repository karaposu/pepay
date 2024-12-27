
# here is db/models/data.py


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


class InitialData(Base):
    __tablename__ = 'initial_data'
    document_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=True)
    family_member_id = Column(Integer, ForeignKey('family_members.family_member_id'), nullable=True)
    raw_data_format = Column(String(20), nullable=False)
    encoded_raw_data = Column(Text, nullable=True)
    binary_data = Column(LargeBinary, nullable=True)  # For other file types

    associated_with = Column(String(50), nullable=False)
    bank_id = Column(Integer, nullable=False)
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)
    number_of_records = Column(Integer, nullable=True)  # Initially empty
    number_of_duplicate_records = Column(Integer, nullable=True)  # Initially empty
    records_df = Column(Text, nullable=True)  # Will hold a serialized DataFrame later
    upload_timestamp = Column(DateTime, default=get_current_time)
    currency = Column(String, nullable=True)
    country_code = Column(String, nullable=True)
    # bank_account_id = Column(Integer, nullable=True)
    bank_account_id = Column(Integer, ForeignKey('bank_accounts.bank_account_id'), nullable=True)
    bank_account = relationship('BankAccount', back_populates='initial_data')

    bank_account_alias = Column(String(100), nullable=True)
    number_of_processed_records = Column(Integer, nullable=True)
    process_status = Column(String(50), nullable=False, default='not started')  # e.g., 'in progress', 'completed', 'failed'
    process_status_in_percentage = Column(Integer, nullable=False, default=0)
    process_started_at = Column(DateTime, nullable=True)  # When the process was started
    process_completed_at = Column(DateTime, nullable=True)

    remaining_time_estimation = Column(Integer, nullable=True)  # Estimated remaining time seconds
    remaining_time_estimation_str = Column(String(16), nullable=True)  # Estimated remaining time in "MM:SS" format
    number_of_cantcategorized = Column(Integer, nullable=True)

    # Relationships
    user = relationship("User", back_populates="uploads", foreign_keys=[user_id])
    family_member = relationship("FamilyMember", back_populates="initial_data", foreign_keys=[family_member_id])
    processed_data = relationship("ProcessedData", back_populates="document")

    __table_args__ = (
        CheckConstraint(
            '((user_id IS NOT NULL AND family_member_id IS NULL) OR (user_id IS NULL AND family_member_id IS NOT NULL))',
            name='chk_initialdata_uploader'
        ),
    )



class ProcessedData(Base):
    __tablename__ = 'processed_data'
    record_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=True)
    family_member_id = Column(Integer, ForeignKey('family_members.family_member_id'), nullable=True)
    document_id = Column(Integer, ForeignKey('initial_data.document_id'), nullable=False)
    # bank_account_id = Column(Integer, nullable=True)
    text = Column(Text, nullable=False)
    cleaned_text = Column(Text, nullable=True)
    amount = Column(Float, nullable=False)
    amount_in_dollar = Column(Float, nullable=False)
    amount_in_gold = Column(Float, nullable=False)
    amount_in_chf = Column(Float, nullable=False)
    currency = Column(Text, nullable=True)
    keyword = Column(String(100), nullable=True)
    rationale = Column(Text, nullable=True)
    refiner_output = Column(Text, nullable=True)
    categorization_result = Column(String(100), nullable=True)
    category = Column(String(50), nullable=True)
    subcategory = Column(String(50), nullable=True)
    categorized_by = Column(String(50), nullable=True)
    loaded_from_keyword_cache = Column(Boolean, default=False, nullable=False)
    record_date = Column(DateTime, nullable=False)
    is_duplicate = Column(Boolean, default=False, nullable=False)

    associated_with = Column(String(50), nullable=False)
    processed_at = Column(DateTime, default=get_current_time)
    is_active = Column(Boolean, default=True, nullable=False)
    backup_category = Column(String(50), nullable=True)
    backup_subcategory = Column(String(50), nullable=True)
    parent_record_id = Column(Integer, ForeignKey('processed_data.record_id'), nullable=True)
    split_level = Column(Integer, default=0, nullable=False)
    is_split = Column(Boolean, default=False, nullable=False)
    apply_to_similar_records = Column(Boolean, default=False, nullable=True)

    attached_file = Column(LargeBinary, nullable=True)
    attached_file_name = Column(String(255), nullable=True)
    attached_file_type = Column(String(50), nullable=True)

    matched_auto_trigger_keyword = Column(String(50), nullable=True)
    matched_metapattern = Column(String(50), nullable=True)

    tax_deductable = Column(Boolean, default=False, nullable=True)
    source_of_income = Column(Boolean, default=False, nullable=True)

    transfer_to_self = Column(Boolean, default=False, nullable=True)
    vetted_by_user = Column(Boolean, default=False, nullable=True)
    transfer_to_saving = Column(Boolean, default=False, nullable=True)

    bank_account_id = Column(Integer, ForeignKey('bank_accounts.bank_account_id'), nullable=True)
    bank_account = relationship('BankAccount', back_populates='processed_data')

    # Relationships
    user = relationship("User", back_populates="processed_data", foreign_keys=[user_id])
    family_member = relationship("FamilyMember", back_populates="processed_data", foreign_keys=[family_member_id])
    document = relationship("InitialData", back_populates="processed_data")

    __table_args__ = (
        CheckConstraint(
            '((user_id IS NOT NULL AND family_member_id IS NULL) OR (user_id IS NULL AND family_member_id IS NOT NULL))',
            name='chk_processeddata_owner'
        ),
    )

    def attach_file(self, file_data: bytes, file_name: str, file_type: str):
        """
        Method to attach a file to the record.
        :param file_data: Binary data of the file.
        :param file_name: Name of the file (e.g., 'document.pdf').
        :param file_type: Type of the file (e.g., 'application/pdf' for PDF or 'image/png' for PNG).
        """
        self.attached_file = file_data
        self.attached_file_name = file_name
        self.attached_file_type = file_type



class MonthlyAggregations(Base):
    __tablename__ = 'monthly_aggregations'
    agg_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    month = Column(String(20), nullable=False)
    category_totals = Column(JSON, nullable=False)
    subcategory_totals = Column(JSON, nullable=False)
    generated_at = Column(DateTime, default=get_current_time)

    user = relationship("User", back_populates="monthly_aggregations")

