# impl/services/file_retriever_service.py

import logging
from fastapi import HTTPException
from traceback import format_exc

logger = logging.getLogger(__name__)


from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Union


class FileData(BaseModel):
    document_id: int
    user_id: int
    raw_data_format: str
    associated_with: Optional[str]
    upload_timestamp: datetime
    process_status: Optional[str] = None
    process_status_in_percentage: Optional[int] = None
    process_started_at: Optional[datetime] = None
    process_completed_at: Optional[datetime] = None
    remaining_time_estimation: Optional[Union[int, float]] = None
    number_of_records: Optional[int] = None
    number_of_processed_records: Optional[int] = 0
    start_date:Optional[any] = None
    end_date: Optional[any] = None
    # Add other fields as necessary

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True
    }

class FileListPaginationRetriever:
    def __init__(self, request, dependencies):
        self.request = request
        self.dependencies = dependencies
        self.response = None

        logger.debug("Inside FileListPaginationRetriever")

        self.preprocess_request_data()
        self.process_request()

    def preprocess_request_data(self):
        user_id = self.request.user_id

        limit=self.request.limit
        offset=self.request.offset
        bank_name=self.request.bank_name

        logger.debug("Inside preprocess_request_data")
        logger.debug(f"user_id: {user_id}")

        try:
            # Access session_factory and file_repository providers from dependencies
            logger.debug("Accessing session_factory and file_repository providers")
            session_factory = self.dependencies.session_factory()
            file_repository_provider = self.dependencies.file_repository

            # Create a new database session
            session = session_factory()
            try:
                logger.debug("Now inside the database session")
                # Instantiate the FileRepository with the session
                file_repository = file_repository_provider(session=session)

                # Get the list of files
                logger.debug(f"Retrieving files for user_id: {user_id}")


                files, total = file_repository.list_files_pagination(user_id, offset, limit , bank_name )

                # logger.debug(f"-------      Files retrieved: {files}")

                # files_data = [FileData.model_validate(file, from_attributes=True) for file in files]
                from models.bank_file import BankFile
                files_data = [BankFile.model_validate(file) for file in files]
                # logger.debug(f"-------      files_data retrieved: {files_data}")

                from models.get_paginated_files200_response import GetPaginatedFiles200Response


                response=GetPaginatedFiles200Response(files= files_data, total=total)
                self.preprocessed_data = response

            except Exception as e:
                session.rollback()
                logger.error(f"An error occurred during file retrieval: {e}\n{format_exc()}")
                raise HTTPException(status_code=500, detail="Internal server error")
            finally:
                session.close()

        except HTTPException as http_exc:
            # Re-raise HTTP exceptions to be handled by FastAPI
            raise http_exc

        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}\n{format_exc()}")
            raise HTTPException(status_code=500, detail="Internal server error")



    def process_request(self):
        # Prepare the response
        self.response = self.preprocessed_data
