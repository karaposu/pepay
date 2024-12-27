# impl/services/record_category_updater_service.py

import logging
from fastapi import HTTPException
from traceback import format_exc

# from models.update_record_response import UpdateRecordResponse

logger = logging.getLogger(__name__)

class RecordCategoryUpdaterService:
    def __init__(self, request, dependencies):
        self.request = request
        self.dependencies = dependencies
        self.response = None

        logger.debug("Inside RecordCategoryUpdaterService")

        self.preprocess_request_data()
        self.process_request()

    def preprocess_request_data(self):
        logger.debug("Inside preprocess_request_data")

        try:
            # Extract parameters from request
            record_id = self.request.record_id
            category = self.request.category
            subcategory = self.request.subcategory
            apply_to_similar_records = self.request.apply_to_similar_records

            logger.debug(f"record_id: {record_id}")
            logger.debug(f"category: {category}")
            logger.debug(f"subcategory: {subcategory}")
            logger.debug(f"apply_to_similar_records: {apply_to_similar_records}")

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

                # Prepare the updates
                updates = {
                    "category": category,
                    "subcategory": subcategory,
                    "categorized_by": "user",
                }

                # Update the record
                logger.debug(f"Updating record with record_id: {record_id}")

                record_repository.update_record(
                    record_id=record_id,
                    updates=updates,
                    # apply_to_similar_records=apply_to_similar_records
                )
                # record_repository.update_record_category(
                #     record_id=record_id,
                #     updates=updates,
                #     apply_to_similar_records=apply_to_similar_records
                # )
                logger.debug("Record updated successfully")

                session.commit()
                self.preprocessed_data = "Record updated successfully"

            except HTTPException as http_exc:
                session.rollback()
                logger.error(f"HTTPException during record update: {http_exc.detail}")
                raise http_exc

            except Exception as e:
                session.rollback()
                logger.error(f"An error occurred during record update: {e}\n{format_exc()}")
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
        # self.response = UpdateRecordResponse(message=self.preprocessed_data)

        self.response = {"message":"Done"}
