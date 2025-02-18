# services/bank_info_retriever_service.py

import logging
from fastapi import HTTPException
from traceback import format_exc


from impl.utils import  create_pepay_db_session

logger = logging.getLogger(__name__)

class BuyPepecoinOrderingService:
    def __init__(self, user_id, request, dependencies):
        self.request = request
        self.user_id = user_id
        self.dependencies = dependencies
        self.response = None
        
        logger.debug("Inside BuyPepecoinOrderingService")
        
        self.preprocess_request_data()
        self.process_request()
        
    def preprocess_request_data(self):
        logger.debug("Inside preprocess_request_data")
        
        try:
            # Extract parameters from request
            supported = self.request.supported
            country = self.request.country

            logger.debug(f"supported: {supported}")
            logger.debug(f"country: {country}")
            
            session= create_pepay_db_session(self.dependencies)
            buypepecoin_repository_provider = self.dependencies.buypepecoin_repository_provider
            
            try:
                logger.debug("Now inside the database session")
                
                # Instantiate the BankInformationRepository with the session
                buypepecoin_repository = buypepecoin_repository_provider(session=session)
                logger.debug("bank_information_repository created")

                # Generate the bank information using the BankInformationRepository
                banks = buypepecoin_repository.save_initial_request_to_transfer_builder(
                    country=country,
                    supported=supported
                )

                self.preprocessed_data = banks

                # Commit the session if necessary
                session.commit()

            except HTTPException as http_exc:
                session.rollback()
                logger.error(f"HTTPException during bank information retrieval: {http_exc.detail}")
                raise http_exc

            except Exception as e:
                session.rollback()
                logger.error(f"An error occurred during bank information retrieval: {e}\n{format_exc()}")
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
        # Set the response to the preprocessed data
        self.response = self.preprocessed_data

