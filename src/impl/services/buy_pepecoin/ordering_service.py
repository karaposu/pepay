# services/buy_pepecoin/ordering_service.py

import logging
from fastapi import HTTPException
from traceback import format_exc

from impl.utils import create_pepay_db_session
from models.buy_pepecoin_order_post_request import BuyPepecoinOrderPostRequest
from models.buy_pepecoin_order_post200_response import BuyPepecoinOrderPost200Response

logger = logging.getLogger(__name__)
# life is in essence is pain that never ends. And in some moments we are relieved fron this pain just a little but and we call this 
# moements happyness. Yet they are far from it. No true happyness in this life for me. I never had luck it with. 
# if you say you are truly happy then i wont believe you are human after all. to be is to suffer. And I exist. 

class BuyPepecoinOrderingService:
    def __init__(self, user_id: int, request: BuyPepecoinOrderPostRequest, dependencies):
        """ 
        :param user_id: The user's ID making the buy request
        :param request: The full buy-pepecoin order request (fe_incall_time, give, take, etc.)
        :param dependencies: DI container with your repository providers
        """
        self.request = request
        self.user_id = user_id
        self.dependencies = dependencies
        self.response: BuyPepecoinOrderPost200Response = None
        
        logger.debug("Inside BuyPepecoinOrderingService")
        
        self.preprocess_request_data()
        self.process_request()
        
    def preprocess_request_data(self):
        logger.debug("Inside preprocess_request_data")
        
        # You can do additional checks/manipulations here if needed.
        # For example:
        # if not self.request.give_amount and not self.request.take_amount:
        #     raise HTTPException(status_code=400, detail="Must specify either give_amount or take_amount.")

        try:
            session = create_pepay_db_session(self.dependencies)
            buypepecoin_repository_provider = self.dependencies.buypepecoin_repository_provider
            
            try:
                logger.debug("Now inside the database session")
                
                # Create the repository with the session
                buypepecoin_repository = buypepecoin_repository_provider(session=session)
                logger.debug("buypepecoin_repository created")

                # Save the buy request to the DB; 
                # this method now returns a BuyPepecoinOrderPost200Response.
                order_response = buypepecoin_repository.save_initial_request_to_transfer_builder(
                    user_id=self.user_id,
                    buy_pepecoin_order_post_request=self.request
                )

                # Store that in self.preprocessed_data (or directly in self.response)
                self.preprocessed_data = order_response

                session.commit()

            except HTTPException as http_exc:
                session.rollback()
                logger.error(f"HTTPException during buy-pepecoin save: {http_exc.detail}")
                raise http_exc

            except Exception as e:
                session.rollback()
                logger.error(f"An error occurred while saving the buy-pepecoin request: {e}\n{format_exc()}")
                raise HTTPException(status_code=500, detail="Internal server error")
            
            finally:
                session.close()

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}\n{format_exc()}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def process_request(self):
        # We’ll just assign the "order_response" from the DB to our final response.
        self.response = self.preprocessed_data
