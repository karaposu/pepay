# impl/services/record_eraser_service.py

import logging
from fastapi import HTTPException
from traceback import format_exc

logger = logging.getLogger(__name__)

class RecordEraserService:
    def __init__(self, request, dependencies):
        self.request = request
        self.dependencies = dependencies
        self.response = None

        logger.debug("Inside RecordEraserService")

        self.preprocess_request_data()
        self.process_request()

    def preprocess_request_data(self):
        record_id = self.request.record_id

        logger.debug("Inside preprocess_request_data")
        logger.debug(f"record_id: {record_id}")

        try:
            # Access session_factory and record_repository from dependencies
            logger.debug("Accessing session_factory and record_repository from dependencies")
            session_factory = self.dependencies.session_factory()
            record_repository_provider = self.dependencies.record_repository

            # Create a new database session
            session = session_factory()
            try:
                logger.debug("Now inside the database session")

                # Instantiate the RecordRepository with the session
                record_repository = record_repository_provider(session=session)

                # Delete the record
                logger.debug(f"Deleting record with record_id: {record_id}")
                record_repository.delete_record(record_id)
                logger.debug("Record deleted successfully")

                session.commit()
                self.preprocessed_data = "Record deleted successfully"

            except HTTPException as http_exc:
                session.rollback()
                logger.error(f"HTTPException during record deletion: {http_exc.detail}")
                raise http_exc

            except Exception as e:
                session.rollback()
                logger.error(f"An error occurred during record deletion: {e}\n{format_exc()}")
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
        self.response = {"msg": self.preprocessed_data}
