# db/repositories/file_repository.py

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from fastapi import HTTPException
import logging
from io import StringIO
import pandas as pd

from db.models import InitialData, ProcessedData
from db.repositories.exchange_rate_repository import ExchangeRateRepository

import tempfile
import os

def get_current_time():
    return datetime.now()

logger = logging.getLogger(__name__)

class FileRepository:
    def __init__(self, session: Session):
        self.session = session
        # self.exchange_rate_repository = exchange_rate_repository




    def get_categorization_status(self, user_id: int, file_id: int):
        # Retrieve the InitialData record for the given user_id and file_id
        initial_data = self.session.query(InitialData).filter_by(user_id=user_id, document_id=file_id).first()

        if initial_data:
            # Prepare the status data
            remaining_time_estimation = initial_data.remaining_time_estimation or 0
            remaining_time_estimation_str = initial_data.remaining_time_estimation_str
            status_in_percentage = initial_data.process_status_in_percentage
            status = initial_data.process_status
            num_records = initial_data.number_of_records
            number_of_processed_records = initial_data.number_of_processed_records or 0
            upload_timestamp = initial_data.upload_timestamp.isoformat() if initial_data.upload_timestamp else None

            # Create a dictionary with the status data
            status_data = {
                'remaining_time_estimation': int(remaining_time_estimation),
                'remaining_time_estimation_str': remaining_time_estimation_str,
                'status_in_percentage': status_in_percentage,
                'status': status,
                'num_records': num_records,
                'number_of_processed_records': number_of_processed_records,
                'upload_timestamp': upload_timestamp
            }

            return status_data
        else:
            logger.error(f"File with id {file_id} for user {user_id} not found")
            raise HTTPException(status_code=404, detail="File not found")

    def save_raw_binary_to_db(self,
                              bank_name,
                              bank_id,
                              user_id,
                              currency,
                              country_code,
                              binary_file,
                              extension) -> int:
        file_data = binary_file  # Use the binary file data directly

        # Store the binary data directly for all file types
        initial_data_entry = InitialData(
            user_id=user_id,
            raw_data_format=extension,
            binary_data=file_data,
            associated_with=bank_name,
            bank_id=bank_id,
            upload_timestamp=get_current_time(),
            currency=currency,
            country_code=country_code
        )

        self.session.add(initial_data_entry)
        self.session.commit()
        return initial_data_entry.document_id

    # def save_raw_binary_to_db(self,
    #                           bank_name,
    #                           bank_id,
    #                           user_id,
    #                           currency,
    #                           country_code,
    #                           binary_file,
    #                           extension) -> int:
    #     file_data = binary_file  # Use the binary file data directly
    #
    #     if extension == 'pdf':
    #         # For PDFs, you may need to decode the binary data
    #         try:
    #             encoded_raw_data = file_data.decode('latin-1')
    #         except UnicodeDecodeError as e:
    #             logger.error(f"Error decoding PDF file data: {e}")
    #             raise HTTPException(status_code=400, detail="Failed to decode PDF file data")
    #
    #         initial_data_entry = InitialData(
    #             user_id=user_id,
    #             raw_data_format='pdf',
    #             encoded_raw_data=encoded_raw_data,
    #             associated_with=bank_name,
    #             bank_id=bank_id,
    #             upload_timestamp=get_current_time(),
    #             currency=currency,
    #             country_code=country_code,
    #         )
    #
    #     elif extension in ['xlsx', 'xls', 'csv']:
    #         initial_data_entry = InitialData(
    #             user_id=user_id,
    #             raw_data_format=extension,
    #             binary_data=file_data,
    #             associated_with=bank_name,
    #             bank_id=bank_id,
    #             upload_timestamp=get_current_time(),
    #             currency=currency,
    #             country_code=country_code
    #         )
    #     else:
    #         raise ValueError(f"Unsupported file format: {extension}")
    #
    #     self.session.add(initial_data_entry)
    #     self.session.commit()
    #     return initial_data_entry.document_id




    def get_file_by_user_and_file_id(self, user_id: int, file_id: int) -> InitialData:
        file_record = self.session.query(InitialData).filter_by(user_id=user_id, document_id=file_id).first()
        return file_record

    def delete_file(self, user_id: int, file_id: int, delete_records=True):
        file_to_delete = self.get_file_by_user_and_file_id(user_id, file_id)
        if not file_to_delete:
            logger.error(f"File with id {file_id} for user {user_id} not found")
            raise HTTPException(status_code=404, detail="File not found")

        if delete_records:
            # Delete associated ProcessedData records
            self.session.query(ProcessedData).filter_by(document_id=file_id).delete()
        else:
            # Check if there are any associated ProcessedData records
            count = self.session.query(ProcessedData).filter_by(document_id=file_id).count()
            if count > 0:
                logger.error(f"Cannot delete file {file_id} because there are associated ProcessedData records")
                raise HTTPException(
                    status_code=400,
                    detail="Cannot delete file because there are associated records. Set delete_records=True to delete them."
                )

        self.session.delete(file_to_delete)
        self.session.commit()
        logger.info(f"File with id {file_id} for user {user_id} deleted successfully")

    # def delete_file(self, user_id: int, file_id: int, delete_records=True):
    #
    #     file_to_delete = self.get_file_by_user_and_file_id(user_id, file_id)
    #     if not file_to_delete:
    #         logger.error(f"File with id {file_id} for user {user_id} not found")
    #         raise HTTPException(status_code=404, detail="File not found")
    #
    #     self.session.delete(file_to_delete)
    #     self.session.commit()
    #     logger.info(f"File with id {file_id} for user {user_id} deleted successfully")

    def should_log_progress(self, number_of_processed_records: int, total_records: int, n: int = 1) -> bool:
        return (number_of_processed_records % n == 0) or (number_of_processed_records == total_records)

    def log_progress(
            self,
            current_record: int,
            total_records: int,
            progress_percentage: float,
            remaining_time_seconds: int,
            remaining_time_str: str,
            user_id: int,
            file_id: int
    ):
        if self.should_log_progress(current_record, total_records):
            logger.debug(
                f"Processed {current_record}/{total_records} records ({progress_percentage:.2f}% complete), "
                f"remaining time: {remaining_time_str}"
            )

            try:
                selected_file_row = self.get_file_by_user_and_file_id(user_id, file_id)

                if selected_file_row:
                    selected_file_row.number_of_processed_records = current_record
                    selected_file_row.process_status_in_percentage = int(progress_percentage)
                    if remaining_time_seconds is not None:
                        selected_file_row.remaining_time_estimation = remaining_time_seconds  # Store remaining time in seconds
                        selected_file_row.remaining_time_estimation_str = remaining_time_str  # Optionally store the formatted string
                    self.session.add(selected_file_row)
                    self.session.commit()
                    logger.debug(f"Updated progress for file_id {file_id}")
                else:
                    logger.error(f"File with id {file_id} for user {user_id} not found")
                    raise HTTPException(status_code=404, detail="File not found")
            except Exception as e:
                logger.error(f"Error logging progress: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail="Failed to log progress")

    def update_processing_status(
            self,
            user_id: int,
            file_id: int,
            process_status: str = None,
            percentage: int = None,
            started_at: datetime = None,
            completed_at: datetime = None,
            remaining_time: int = None
    ):
        selected_file_row = self.get_file_by_user_and_file_id(user_id, file_id)

        if selected_file_row:
            if process_status is not None:
                selected_file_row.process_status = process_status
            if percentage is not None:
                selected_file_row.process_status_in_percentage = percentage
            if started_at is not None:
                selected_file_row.process_started_at = started_at
            if completed_at is not None:
                selected_file_row.process_completed_at = completed_at
            if remaining_time is not None:
                selected_file_row.remaining_time_estimation = remaining_time

            self.session.add(selected_file_row)
            self.session.commit()
            logger.info(f"Updated processing status for file_id {file_id} to {process_status}")
            logger.debug(f"Process status for file_id {file_id}: {selected_file_row.process_status}")
        else:
            logger.error(f"File with id {file_id} for user {user_id} not found")
            raise HTTPException(status_code=404, detail="File not found")

    def list_files(self, user_id: int):
        files = self.session.query(InitialData).filter(InitialData.user_id == user_id).all()
        return files

    def list_files_pagination(self, user_id: int, offset: int = 0, limit: int = 10, bank_name: str = None):
        # Build the base query
        if offset is None:
            offset= 0
        if offset < 0:
            offset = 0
        if limit <= 0:
            limit = 1  # Set a default limit if invalid

        query = self.session.query(InitialData).filter(InitialData.user_id == user_id)

        # Apply bank_name filter if provided
        if bank_name:
            query = query.filter(InitialData.associated_with == bank_name)

        # Get the total count before applying pagination
        total = query.count()

        # Apply ordering, offset, and limit for pagination
        files = query.order_by(InitialData.upload_timestamp.desc()).offset(offset).limit(limit).all()

        return files, total

    # def list_files_pagination(self, user_id: int, offset: int = 0, limit: int = 10):
    #     # Validate offset and limit
    #     if offset < 0:
    #         offset = 0
    #     if limit <= 0:
    #         limit = 10  # Set a default limit if invalid
    #
    #     # Query to get total count
    #     total = self.session.query(InitialData).filter(InitialData.user_id == user_id).count()
    #
    #     # Query to get paginated files
    #     files_query = (
    #         self.session.query(InitialData)
    #         .filter(InitialData.user_id == user_id)
    #         .order_by(InitialData.upload_timestamp.desc())
    #         .offset(offset)
    #         .limit(limit)
    #     )
    #     files = files_query.all()
    #
    #     return files, total

    def save_statements_df_to_db(
            self,
            user_id: int,
            start_date_str: str,
            end_date_str: str,
            num_records: int,
            records_df_serialized: str,
            exchange_rate_repository: ExchangeRateRepository
    ):
        last_entry = self.session.query(InitialData).filter_by(user_id=user_id).order_by(
            InitialData.document_id.desc()).first()

        if last_entry:
            last_entry.end_date = end_date_str
            last_entry.start_date = start_date_str
            last_entry.number_of_records = num_records
            last_entry.records_df = records_df_serialized

            self.session.add(last_entry)
            self.session.commit()
            logger.debug("Extracted dataframe is being transferred to processed data table")

            # Transfer data to processed table
            self.transfer_df_to_processed_table(
                document_id=last_entry.document_id,
                exchange_rate_repository=exchange_rate_repository,
                remove_duplicate_records=True
            )
        else:
            logger.error("No initial data entry found to save statements")
            raise HTTPException(status_code=404, detail="No initial data entry found")

    def exchange_rates_to_amounts(self, amount, exchange_rates, amount_is_usd=False):
        rate_to_usd = exchange_rates['rate_to_usd']
        usd_to_gold_rate = exchange_rates['usd_to_gold_rate']
        usd_to_chf_rate = exchange_rates['usd_to_chf_rate']

        amount_in_dollar = amount / rate_to_usd  # Converting to USD
        amount_in_gold = amount / (rate_to_usd * (1 / usd_to_gold_rate))  # Converting to Gold

        amount_in_chf = (amount / rate_to_usd) / usd_to_chf_rate

        return amount_in_dollar, amount_in_gold, amount_in_chf

    def is_duplicate_record(self, user_id: int, record_date_str: str, record_amount: float, record_text: str,
                            current_file_id: int) -> bool:
        """
        Check if there is an existing processed record that matches the given fields.
        Exclude records with the same file_id (as they're the same file).
        """
        # logger.debug(f"record_date_str: {record_date_str}")
        record_date = datetime.strptime(record_date_str, "%Y-%m-%d")

        # logger.debug(f"record_date_str: {record_date_str}")
        existing_record = self.session.query(ProcessedData).filter(
            ProcessedData.user_id == user_id,
            ProcessedData.record_date == record_date,
            ProcessedData.amount == record_amount,
            ProcessedData.text == record_text,
            ProcessedData.document_id != current_file_id
        ).first()

        return existing_record is not None

    def transfer_df_to_processed_table(self,
                                       document_id: int,
                                       exchange_rate_repository: ExchangeRateRepository,
                                       remove_duplicate_records: bool = False):
        initial_data_record = self.session.query(InitialData).filter(InitialData.document_id == document_id).first()
        if not initial_data_record:
            raise ValueError(f"No InitialData record found for document_id {document_id}")

        # Initialize a counter for duplicate records
        self.number_of_duplicate_records = 0

        records_df = pd.read_json(StringIO(initial_data_record.records_df))

        for _, row in records_df.iterrows():
            raw_row_values = row.to_dict()

            user_id = initial_data_record.user_id
            record_date_obj = raw_row_values.get('date')
            record_text = raw_row_values.get('text', '')
            record_amount = raw_row_values.get('amount', 0)
            record_currency = raw_row_values.get('currency', '')

            # Ensure record_date_obj is a datetime
            if isinstance(record_date_obj, str):
                record_date_obj = datetime.strptime(record_date_obj, "%Y-%m-%d")

            record_date_str = record_date_obj.strftime("%Y-%m-%d")
            # Validate the date format to ensure it's in YYYY-MM-DD
            try:
                datetime.strptime(record_date_str, "%Y-%m-%d")
            except ValueError:
                logger.error(f"Invalid date format for record: {record_date_str}. Expected format: YYYY-MM-DD")
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid date format: {record_date_str}. Expected format: YYYY-MM-DD"
                )

            #logger.debug("Now exchange rates will be added to each record")

            # Use the provided exchange_rate_repository
            exchange_rates = exchange_rate_repository.get_or_update_exchange_rate(record_date_str, record_currency)
            #logger.debug(f"exchange_rates: {exchange_rates}")
            amount_in_dollar, amount_in_gold, amount_in_chf = self.exchange_rates_to_amounts(record_amount,
                                                                                             exchange_rates,
                                                                                             amount_is_usd=False)

            is_duplicate_record_flag = False
            if remove_duplicate_records:
                # Check if the record is a duplicate
                is_duplicate_record_flag = self.is_duplicate_record(user_id, record_date_str, record_amount,
                                                                    record_text, initial_data_record.document_id)
                if is_duplicate_record_flag:
                    logger.debug(
                        f"Marking duplicate record: user_id={user_id}, date={record_date_str}, amount={record_amount}, text={record_text}"
                    )
                    self.number_of_duplicate_records += 1

            processed_data_record = ProcessedData(
                user_id=initial_data_record.user_id,
                document_id=initial_data_record.document_id,
                text=record_text,
                cleaned_text=raw_row_values.get('cleaned_text', ''),
                keyword=raw_row_values.get('keyword', ''),
                amount=record_amount,
                amount_in_dollar=amount_in_dollar,
                amount_in_gold=amount_in_gold,
                amount_in_chf=amount_in_chf,
                currency=record_currency,
                record_date=record_date_obj,
                associated_with=initial_data_record.associated_with,
                # Mark the record as duplicate if needed
                is_duplicate=is_duplicate_record_flag
            )
            self.session.add(processed_data_record)

        self.session.commit()
        logger.info(f"ProcessedData table updated successfully for document_id {document_id}")

        # Log the count of duplicate records if duplicates were checked
        if remove_duplicate_records:
            logger.info(f"Number of duplicate records marked: {self.number_of_duplicate_records}")
