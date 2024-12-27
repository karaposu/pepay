# impl/services/file/upload_file_service.py





import logging
from fastapi import HTTPException
from datetime import datetime
import os
import tempfile
from traceback import format_exc

from models.upload_and_process_pdf200_response import UploadAndProcessPdf200Response
from bsd_analyser.extractors import get_extractor


logger = logging.getLogger(__name__)

import yaml


def get_currencies_by_country(yaml_file_path, country_code):

    try:
        with open(yaml_file_path, 'r', encoding='utf-8') as file:
            country_currency_data = yaml.safe_load(file)

        # Normalize the country code to uppercase to ensure case-insensitive matching
        country_code = country_code.upper()

        logger.debug(f"--------------------------country_code {country_code}")
        logger.debug(f"--------------------------country_currency_data {country_currency_data}")

        if country_code in country_currency_data:
            currencies = country_currency_data[country_code].get('currencies')
            if currencies is None:
                print(f"The country code '{country_code}' has no associated currencies.")
                return None
            elif isinstance(currencies, list):
                return currencies[0]
            else:
                # In case 'currencies' is not a list, return it as a single-item list
                return [currencies]
        else:
            print(f"Country code '{country_code}' not found in the YAML file.")
            return None

    except FileNotFoundError:
        print(f"Error: The file '{yaml_file_path}' was not found.")
        return None
    except yaml.YAMLError as exc:
        print(f"Error parsing YAML file: {exc}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None




class UploadFileService:
    def __init__(self, request, dependencies):
        self.request = request
        self.dependencies = dependencies
        self.response = None

        logger.debug("Inside UploadFileService")

        self.preprocess_request_data()
        self.process_request()

        self.is_first_upload=None

    def preprocess_request_data(self):
        user_id = self.request.user_id
        binary_file = self.request.pdf_file

        bank_id = self.request.bank_id
        extension = self.request.extension
        country_code = self.request.country_code
        process_as_test = self.request.process_as_test
        use_auto_extractor = self.request.use_auto_extractor


        logger.debug("Inside preprocess_request_data")
        logger.debug(f"user_id: {user_id}")
        logger.debug(f"extension: {extension}")
        logger.debug(f"process_as_test: {process_as_test}")

        # Validate inputs
        if not isinstance(user_id, int) or user_id <= 0:
            logger.error(f"Invalid user ID: {user_id}")
            raise HTTPException(status_code=400, detail=f"Invalid user ID: {user_id}")

        if not binary_file:
            logger.error("The uploaded file is empty or invalid.")
            raise HTTPException(status_code=400, detail="The uploaded file is empty or invalid.")
        if not isinstance(binary_file, (bytes, bytearray)):
            logger.error("The uploaded file is not in a binary format.")
            raise HTTPException(status_code=400, detail="The uploaded file is not in a binary format.")

        # if not isinstance(bank_name, str) or not bank_name.strip():
        #     logger.error("Invalid bank name provided.")
        #     raise HTTPException(status_code=400, detail="Invalid bank name provided.")

        try:
            # Access session_factory and repositories from dependencies
            logger.debug("Accessing session_factory and repositories from dependencies")
            # session_factory = self.dependencies.session_factory()

            # Access providers from dependencies
            main_session_factory = self.dependencies.session_factory
            exchange_rate_session_factory = self.dependencies.exchange_rate_session_factory
            fixed_info_session_factory = self.dependencies.fixed_info_session_factory

            file_repository_provider = self.dependencies.file_repository
            exchange_rate_repository_provider = self.dependencies.exchange_rate_repository
            user_repository_provider = self.dependencies.user_repository
            bank_information_provider = self.dependencies.bank_information_repository



            # Obtain sessionmakers
            main_sessionmaker = main_session_factory()
            exchange_rate_sessionmaker = exchange_rate_session_factory()
            fixed_info_sessionmaker = fixed_info_session_factory()

            # Create sessions
            main_session = main_sessionmaker()
            exchange_rate_session = exchange_rate_sessionmaker()
            fixed_info_session = fixed_info_sessionmaker()

            bank_information_repository = bank_information_provider(session=fixed_info_session)


            try:
                logger.debug("Now inside the database session")

                # Use a temporary directory to save the uploaded file
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_file_path = os.path.join(temp_dir, f"{user_id}_uploaded_file.{extension}")
                    try:
                        with open(temp_file_path, "wb") as temp_file:
                            temp_file.write(binary_file)
                        logger.debug(f"File saved to temporary path: {temp_file_path}")
                    except IOError as e:
                        logger.error(f"Failed to write the temporary file: {e}")
                        raise HTTPException(status_code=500, detail=f"Failed to write the temporary file: {e}")

                    # Process the file using the extractor
                    try:

                        string_bank_id=bank_information_repository.find_bank_with_bank_id(bank_id)
                        # bank = bank_information_repository.find_bank_by_string_id(bank_id)


                        ExtractorClass = get_extractor(string_bank_id)
                        logger.debug(f"Using ExtractorClass: {ExtractorClass.__name__}")
                        logger.debug(f"process_as_test: {process_as_test}")

                        extractor = ExtractorClass(temp_file_path, "TRY", test=process_as_test)
                        extraction_result = extractor.process()
                        logger.debug("File processed successfully")
                    except Exception as e:
                        logger.error(f"Error during file processing: {e}\n{format_exc()}")
                        raise HTTPException(status_code=500, detail=f"Error during file processing: {e}")

                    # Instantiate repositories with the session
                    file_repository = file_repository_provider(session=main_session)
                    user_repository = user_repository_provider(session=main_session)
                    exchange_rate_repository = exchange_rate_repository_provider(session=exchange_rate_session)

                    logger.debug("Checking if this is the first upload for the user")
                    user_files = file_repository.list_files(user_id)
                    if not user_files:
                        # This is the first upload
                        logger.info(f"This is the first upload for user_id: {user_id}")
                        self.is_first_upload = True
                    else:
                        self.is_first_upload = False

                    base_dir = os.path.dirname(__file__)
                    country_to_currency_file_path = os.path.join(base_dir, "..", "..", "..", "assets", "config", "country_to_currency.yaml")
                    country_to_currency_file_path = os.path.abspath(country_to_currency_file_path)


                    country_currency_code=get_currencies_by_country(country_to_currency_file_path, country_code)
                    logger.debug(f"--------------------------country_currency_code {country_currency_code}")

                    if self.is_first_upload:
                        user_repository.update_user_settings(
                            user_id=user_id,
                            default_currency=country_currency_code,
                            default_country=country_code,
                            default_bank=string_bank_id

                        )
                       # user_repository.add_default_currency(user_id, country_currency_code)
                    # pick currency as user's default currency.


                    # whenever we return currency we must also return
                    # curreceny symbol,  where to put the symbol, how many fractuals

                    try:
                        # file extraction result should have a field called
                        # mono_statement

                        logger.debug("Saving raw file to the database")


                        file_id = file_repository.save_raw_file_to_db(
                            file_path=extractor.file_path,
                            bank_name=string_bank_id,
                            bank_id=bank_id,
                            user_id=user_id,
                            currency=country_currency_code,
                            country_code= country_code
                        )


                        logger.debug(f"Raw file saved with file_id: {file_id}")
                    except Exception as e:
                        logger.error(f"Failed to save raw file to the database: {e}\n{format_exc()}")
                        main_session.rollback()
                        raise HTTPException(status_code=500, detail=f"Failed to save raw file to the database: {e}")

                    # Save the statements data to the database
                    try:
                        logger.debug("Saving statements data to the database")
                        logger.debug(f"extraction_result.num_records: {extraction_result.num_records}")

                        file_repository.save_statements_df_to_db(
                            user_id=user_id,
                            start_date_str=extraction_result.start_date_str,
                            end_date_str=extraction_result.end_date_str,
                            num_records=extraction_result.num_records,
                            records_df_serialized=extraction_result.records_df_serialized,
                            exchange_rate_repository=exchange_rate_repository
                        )
                        logger.debug("Statements data saved successfully")
                        main_session.commit()
                        exchange_rate_session.commit()
                    except Exception as e:
                        logger.error(f"Failed to save statements data to the database: {e}\n{format_exc()}")
                        main_session.rollback()
                        exchange_rate_session.rollback()
                        raise HTTPException(status_code=500, detail=f"Failed to save statements data to the database: {e}")

                # Prepare the preprocessed data
                self.preprocessed_data = {
                    "file_id": file_id,
                    "upload_timestamp": datetime.now().isoformat()
                }

            except HTTPException as http_exc:
                main_session.rollback()
                exchange_rate_session.rollback()
                raise http_exc

            except Exception as e:
                main_session.rollback()
                exchange_rate_session.rollback()
                logger.error(f"An error occurred: {e}\n{format_exc()}")
                raise HTTPException(status_code=500, detail="Internal server error")

            finally:
                main_session.close()
                exchange_rate_session.close()

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}\n{format_exc()}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def process_request(self):
        self.response = UploadAndProcessPdf200Response(
            file_id=self.preprocessed_data["file_id"],
            upload_timestamp=self.preprocessed_data["upload_timestamp"]
        )








