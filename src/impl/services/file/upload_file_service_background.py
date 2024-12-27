# impl/services/file/upload_file_service_background.py


import logging
from fastapi import HTTPException
from datetime import datetime
import os
from traceback import format_exc

from models.upload_and_process_pdf200_response import UploadAndProcessPdf200Response
from impl.utils import create_budget_db_session, create_banks_data_db_session, get_currencies_by_country, sanitize_bank_name

import yaml
import re

logger = logging.getLogger(__name__)


class UploadFileBackgroundService:
    def __init__(self, request, dependencies):
        self.request = request
        self.dependencies = dependencies
        self.response = None

        logger.debug("Inside UploadFileBackgroundService")

        self.is_first_upload = None

        self.budget_tracker_session = create_budget_db_session(self.dependencies)
        self.banks_db_session = create_banks_data_db_session(self.dependencies)

        # Repository providers
        self.user_repository_provider = self.dependencies.user_repository
        self.file_repository_provider = self.dependencies.file_repository
        self.bank_information_repository_provider = self.dependencies.bank_information_repository

        try:
            # Instantiate repositories
            self.file_repository = self.file_repository_provider(session=self.budget_tracker_session)
            self.user_repository = self.user_repository_provider(session=self.budget_tracker_session)
            self.bank_information_repository = self.bank_information_repository_provider(session=self.banks_db_session)

            self.preprocess_request_data()
            self.process_request()
        finally:
            # Ensure sessions are closed
            self.budget_tracker_session.close()
            self.banks_db_session.close()

    def validate_inputs(self):
        if not isinstance(self.user_id, int) or self.user_id <= 0:
            logger.error(f"Invalid user ID: {self.user_id}")
            raise HTTPException(status_code=400, detail=f"Invalid user ID: {self.user_id}")

        if not self.binary_file:
            logger.error("The uploaded file is empty or invalid.")
            raise HTTPException(status_code=400, detail="The uploaded file is empty or invalid.")
        if not isinstance(self.binary_file, (bytes, bytearray)):
            logger.error("The uploaded file is not in a binary format.")
            raise HTTPException(status_code=400, detail="The uploaded file is not in a binary format.")

    def get_string_bank_id(self):
        if self.bank_id is None:
            self.bank_id = -1
            if not self.bank_name or not self.bank_name.strip():
                logger.error("Bank name must be provided when bank_id is not specified.")
                raise HTTPException(status_code=400, detail="Bank name must be provided when bank_id is not specified.")

            # Sanitize bank_name to create string_bank_id
            string_bank_id = sanitize_bank_name(self.bank_name)
            if not string_bank_id:
                logger.error("Bank name after sanitization is empty.")
                raise HTTPException(status_code=400, detail="Invalid bank name provided.")

            # Since works_only_with_auto_parser is not applicable when bank_id is None, set it to False
            works_only_with_auto_parser = False
            return string_bank_id, works_only_with_auto_parser
        else:
            try:
                result = self.bank_information_repository.find_bank_with_bank_id(self.bank_id)
                if not result:
                    logger.error("Bank ID cannot be matched in DB.")
                    raise HTTPException(status_code=400, detail="Invalid bank ID provided.")

                string_bank_id, works_only_with_auto_parser = result
                return string_bank_id, works_only_with_auto_parser
            except Exception as e:
                logger.error(f"An error occurred while fetching bank information: {e}\n{format_exc()}")
                raise HTTPException(status_code=500, detail="Internal server error")

    def check_is_first_upload(self):
        user_files = self.file_repository.list_files(self.user_id)
        self.is_first_upload = not user_files
        if self.is_first_upload:
            logger.info(f"This is the first upload for user_id: {self.user_id}")

    def get_country_currency_code(self):
        base_dir = os.path.dirname(__file__)
        country_to_currency_file_path = os.path.join(
            base_dir, "..", "..", "..", "assets", "config", "country_to_currency.yaml"
        )
        country_to_currency_file_path = os.path.abspath(country_to_currency_file_path)
        self.country_currency_code = get_currencies_by_country(country_to_currency_file_path, self.country_code)
        if not self.country_currency_code:
            logger.error(f"Could not find currency for country code: {self.country_code}")
            raise HTTPException(status_code=400, detail="Invalid country code provided.")
        logger.debug(f"Country currency code: {self.country_currency_code}")

    def update_user_settings_if_first_upload(self):
        if self.is_first_upload:
            self.user_repository.update_user_settings(
                user_id=self.user_id,
                default_currency=self.country_currency_code,
                default_country=self.country_code,
                default_bank=self.string_bank_id
            )

    def save_raw_file_to_database(self):
        self.file_id = self.file_repository.save_raw_binary_to_db(
            bank_name=self.string_bank_id,
            bank_id=self.bank_id,
            user_id=self.user_id,
            currency=self.country_currency_code,
            country_code=self.country_code,
            binary_file=self.binary_file,
            extension=self.extension
        )
        logger.debug(f"Raw file saved with file_id: {self.file_id}")

    def start_background_task(self):
        from impl.services.file.background_tasks import process_file_task  # Import the background task function

        self.background_tasks.add_task(
            process_file_task,
            file_id=self.file_id,
            user_id=self.user_id,
            bank_id=self.bank_id,
            country_code=self.country_code,
            process_as_test=self.process_as_test,
            use_auto_extractor=self.use_auto_extractor,
            dependencies=self.dependencies,  # Pass dependencies if needed
            extension=self.extension,
            works_only_with_auto_parser=self.works_only_with_auto_parser
        )

    def preprocess_request_data(self):
        try:
            # Extract request data
            self.user_id = self.request.user_id
            self.binary_file = self.request.pdf_file
            self.bank_id = self.request.bank_id
            self.extension = self.request.extension
            self.country_code = self.request.country_code
            self.process_as_test = self.request.process_as_test
            self.use_auto_extractor = self.request.use_auto_extractor
            self.bank_name = self.request.bank_name
            self.background_tasks = self.request.background_tasks

            logger.debug("Inside preprocess_request_data")
            logger.debug(f"user_id: {self.user_id}")
            logger.debug(f"extension: {self.extension}")
            logger.debug(f"process_as_test: {self.process_as_test}")

            # Validate inputs
            self.validate_inputs()

            # Get string_bank_id and works_only_with_auto_parser
            self.string_bank_id, self.works_only_with_auto_parser = self.get_string_bank_id()

            # Check if this is the first upload for the user
            self.check_is_first_upload()

            # Get country currency code
            self.get_country_currency_code()

            # Update user settings if this is the first upload
            self.update_user_settings_if_first_upload()

            # Save raw file to the database
            self.save_raw_file_to_database()

            # Commit the session
            self.budget_tracker_session.commit()

            # Start the background task
            self.start_background_task()

            # Prepare the preprocessed data
            self.preprocessed_data = {
                "file_id": self.file_id,
                "upload_timestamp": datetime.now().isoformat()
            }

        except HTTPException as http_exc:
            self.budget_tracker_session.rollback()
            raise http_exc
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}\n{format_exc()}")
            self.budget_tracker_session.rollback()
            raise HTTPException(status_code=500, detail="Internal server error")

    def process_request(self):
        self.response = UploadAndProcessPdf200Response(
            file_id=self.preprocessed_data["file_id"],
            upload_timestamp=self.preprocessed_data["upload_timestamp"]
        )
