# impl/services/record_creator_service.py

import logging
from fastapi import HTTPException
from traceback import format_exc

logger = logging.getLogger(__name__)

class RecordCreatorService:
    def __init__(self, request, user_id, dependencies ):
        self.request = request
        self.dependencies = dependencies
        self.user_id = user_id
        self.response = None

        logger.debug("Inside RecordCreatorService")

        self.preprocess_request_data()
        self.process_request()

    def preprocess_request_data(self):
        logger.debug("Inside preprocess_request_data")

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

                # Prepare the record data
                record_data = self.request.dict()
                record_data['user_id'] = self.user_id  # Ensure the user_id is set correctly

                # Create the record
                logger.debug(f"Creating record with data: {record_data}")
                record_id = record_repository.add_record(record_data)
                logger.debug(f"Record created successfully with record_id: {record_id}")

                session.commit()
                self.preprocessed_data = {"record_id": record_id}

            except HTTPException as http_exc:
                session.rollback()
                logger.error(f"HTTPException during record creation: {http_exc.detail}")
                raise http_exc

            except Exception as e:
                session.rollback()
                logger.error(f"An error occurred during record creation: {e}\n{format_exc()}")
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
        self.response = {"record_id": self.preprocessed_data["record_id"]}
