

import logging
from fastapi import HTTPException
from datetime import datetime
from traceback import format_exc

from models.record_data import RecordData

logger = logging.getLogger(__name__)


class RecordsSplitterService:
    def __init__(self, request, dependencies):
        self.request = request
        self.dependencies = dependencies
        self.response = None
        self.preprocess_request_data()
        self.process_request()

    def preprocess_request_data(self):
        logger.debug("Inside preprocess_request_data")

        try:
            # Extract parameters from request
            user_id = self.request.user_id

            #todo validate user_id

            splits = self.request.splits

            from impl.utils import create_budget_db_session
            session= create_budget_db_session(self.dependencies)
            record_repository_provider = self.dependencies.record_repository

            try:
                logger.debug("Now inside the database session")
                record_repository = record_repository_provider(session=session)

                record_repository.split_record(record_id=self.request.record_id, splits=splits)

                self.preprocessed_data = "done"

            except HTTPException as http_exc:
                session.rollback()
                logger.error(f"HTTPException during records retrieval: {http_exc.detail}")
                raise http_exc

            except Exception as e:
                session.rollback()
                logger.error(f"An error occurred during records retrieval: {e}\n{format_exc()}")
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

        self.response = "done"



