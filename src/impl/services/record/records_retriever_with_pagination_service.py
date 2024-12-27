# impl/services/records_retriever_with_pagination_service.py

import logging
from fastapi import HTTPException
from datetime import datetime
from traceback import format_exc

from models.record_data import RecordData
from models.get_filtered_records_with_pagination200_response import GetFilteredRecordsWithPagination200Response

logger = logging.getLogger(__name__)

class RecordsRetrieverWithPaginationService:
    def __init__(self, request, dependencies):
        self.request = request
        self.dependencies = dependencies
        self.response = None

        logger.debug("Inside RecordsRetrieverWithPaginationService")

        self.preprocess_request_data()
        self.process_request()

    def preprocess_request_data(self):
        logger.debug("Inside preprocess_request_data")

        try:
            # Extract parameters from request
            user_id = self.request.user_id
            document_id = self.request.document_id
            start_date = self.request.start_date
            end_date = self.request.end_date
            associated_with = self.request.associated_with
            limit = self.request.limit
            offset = self.request.offset

            sort_by =self.request.sort_by
            order =self.request.order
            keyword_search =self.request.keyword_search
            exact_match =self.request.exact_match
            by_category =self.request.by_category
            by_subcategory =self.request.by_subcategory
            bring_cleaned_text =self.request.bring_cleaned_text
            bring_not_vetted =self.request.bring_not_vetted
            bring_tax_deductible =self.request.bring_tax_deductible
            bring_failed_to_categorize =self.request.bring_failed_to_categorize


            logger.debug(f"user_id: {user_id}")
            logger.debug(f"document_id: {document_id}")
            logger.debug(f"start_date: {start_date}")
            logger.debug(f"end_date: {end_date}")
            logger.debug(f"associated_with: {associated_with}")
            logger.debug(f"limit: {limit}")
            logger.debug(f"offset: {offset}")

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

                # Get records with pagination from the repository
                logger.debug("Retrieving records with pagination from the database")
                records, total_records = record_repository.get_records_with_pagination(
                    user_id=user_id,
                    document_id=document_id,
                    start_date=start_date,
                    end_date=end_date,
                    associated_with=associated_with,
                    limit=limit,
                    offset=offset,

                    sort_by=sort_by,
                    order=order,
                    keyword_search=keyword_search,
                    exact_match=exact_match,
                    by_category=by_category,
                    by_subcategory=by_subcategory,
                    bring_cleaned_text=bring_cleaned_text,
                    bring_not_vetted=bring_not_vetted,
                    bring_tax_deductible=bring_tax_deductible,
                    bring_failed_to_categorize=bring_failed_to_categorize
                )

                logger.debug(f"Number of records retrieved: {len(records)}")
                logger.debug(f"Total records: {total_records}")

                if not records:
                    logger.error("No records found")
                    # raise HTTPException(status_code=404, detail="No records found")

                # Convert records to list of RecordData instances
                record_data_list = [RecordData.from_orm(record) for record in records]


                # Prepare the response
                response = GetFilteredRecordsWithPagination200Response(
                    data=record_data_list,
                    total=total_records
                )

                self.preprocessed_data = response

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
        # Prepare the response
        self.response = self.preprocessed_data
