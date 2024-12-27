# impl/services/file/background_tasks.py

import os
import tempfile
import logging
import traceback
from datetime import datetime

from db.models.data import InitialData
from bsd_analyser.extractors import get_extractor
from impl.utils import create_budget_db_session, create_banks_data_db_session, create_exchange_rate_db_session

logger = logging.getLogger(__name__)

def process_file_task(
    file_id: int,
    user_id: int,
    bank_id: str,
    country_code: str,
    process_as_test: bool,
    use_auto_extractor: bool,
    dependencies,
    extension
):
    logger.debug(f"Processing file_id: {file_id} in background task")

    budget_tracker_session = create_budget_db_session(dependencies)
    banks_db_session = create_banks_data_db_session(dependencies)
    exchange_rate_db_session = create_exchange_rate_db_session(dependencies)

    try:
        # Access repositories
        file_repository_provider = dependencies.file_repository
        exchange_rate_repository_provider = dependencies.exchange_rate_repository
        bank_information_repository_provider = dependencies.bank_information_repository

        file_repository = file_repository_provider(session=budget_tracker_session)
        exchange_rate_repository = exchange_rate_repository_provider(session=exchange_rate_db_session)
        bank_information_repository = bank_information_repository_provider(session=banks_db_session)

        # Retrieve InitialData
        initial_data = budget_tracker_session.query(InitialData).filter_by(document_id=file_id).first()
        if not initial_data:
            logger.error(f"No InitialData found for file_id: {file_id}")
            return

        binary_file = initial_data.binary_data
        if binary_file is None:
            encoded_raw_data = initial_data.encoded_raw_data
            if encoded_raw_data is not None:
                # Encode the string back to bytes
                binary_file = encoded_raw_data.encode('latin-1')  # Use the same encoding used during decoding
            else:
                logger.error(f"No data found for file_id: {file_id}")
                return

        extension = initial_data.raw_data_format

        # Save binary data to a temporary file
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = os.path.join(temp_dir, f"{user_id}_uploaded_file.{extension}")
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(binary_file)
            logger.debug(f"File saved to temporary path: {temp_file_path}")

            if use_auto_extractor:

                # string_bank_id = bank_information_repository.find_bank_with_bank_id(bank_id)
                ExtractorClass = get_extractor("unknown")
                extractor = ExtractorClass(temp_file_path, initial_data.currency, test=process_as_test)
                extraction_result = extractor.process()
                logger.debug("File processed successfully")

            else:

            # Process the file using the extractor
                string_bank_id = bank_information_repository.find_bank_with_bank_id(bank_id)
                ExtractorClass = get_extractor(string_bank_id)
                extractor = ExtractorClass(temp_file_path, initial_data.currency, test=process_as_test)
                extraction_result = extractor.process()
                logger.debug("File processed successfully")

            # Save extracted data to the database
            file_repository.save_statements_df_to_db(
                user_id=user_id,
                start_date_str=extraction_result.start_date_str,
                end_date_str=extraction_result.end_date_str,
                num_records=extraction_result.num_records,
                records_df_serialized=extraction_result.records_df_serialized,
                exchange_rate_repository=exchange_rate_repository
            )

            # Update InitialData status
            initial_data.process_status = 'extracted'
            # initial_data.process_status_in_percentage = 100
            # initial_data.process_completed_at = datetime.utcnow()
            initial_data.number_of_records = extraction_result.num_records

            budget_tracker_session.commit()
            exchange_rate_db_session.commit()

    except Exception as e:
        logger.error(f"Error processing file_id {file_id}: {e}\n{traceback.format_exc()}")
        budget_tracker_session.rollback()
        exchange_rate_db_session.rollback()
        # Update InitialData to reflect the error
        initial_data.process_status = 'failed'
        budget_tracker_session.commit()
    finally:
        budget_tracker_session.close()
        exchange_rate_db_session.close()
        banks_db_session.close()
