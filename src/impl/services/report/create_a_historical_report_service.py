# impl/services/report/create_a_historical_report_service.py


import logging
from fastapi import HTTPException
from traceback import format_exc

from models.historical_aggregation import HistoricalAggregation, CategoryAggregation
from impl.utils import create_budget_db_session, create_banks_data_db_session, get_currencies_by_country, sanitize_bank_name


logger = logging.getLogger(__name__)

class CreateAHistoricalReportService:
    def __init__(self, request, dependencies):
        self.request = request
        self.dependencies = dependencies
        self.response = None
        self.currency_configs = dependencies.currency_configs()


        logger.debug("Inside HistoricalReportMaker")

        self.preprocess_request_data()
        self.process_request()

    def preprocess_request_data(self):
        logger.debug("Inside preprocess_request_data")

        try:
            # Extract parameters from request
            user_id = self.request.user_id
            bank_account_id = self.request.bank_account_id
            start_date=self.request.start_date 
            end_date=self.request.end_date 

            logger.debug(f"user_id: {user_id}")
            logger.debug(f"bank_account_id: {bank_account_id}")

            self.budget_tracker_session = create_budget_db_session(self.dependencies)

            # Access session_factory and report_repository from dependencies
            logger.debug("Accessing session_factory and report_repository from dependencies")

            user_repository_provider = self.dependencies.user_repository
    
            report_repository_provider = self.dependencies.report_repository

        

            try:
                logger.debug("Now inside the database session")

                user_repository = user_repository_provider(session=self.budget_tracker_session)
                report_repository = report_repository_provider(
                    session=self.budget_tracker_session,
                    currency_configs=self.currency_configs,
                    user_repository=user_repository
                )

               

                # Define the master category list
                master_category_list = {
                    "Food & Dining": ["Groceries", "Restaurants", "Coffee", "Takeout"],
                    "Utilities": ["Electricity and Water and Gas", "Internet and Mobile"],
                    "Accommodation": ["Accommodation"],
                    "Incoming P2P Transfers": ["Incoming Money"],
                    "Outgoing P2P Transfers": ["Outgoing Money"],
                    "Cash Withdrawal": ["Cash Withdrawal"],
                    "Cash Deposit": ["Cash Deposit"],
                    "Transportation": ["Fuel", "Taxi", "Travel Tickets", "Public Transportation", "Vehicle Maintenance", "Car Payments"],
                    "Healthcare": ["Medical Bills", "Health Insurance", "Medications"],
                    "Retail Purchases": ["Clothes", "Technology Items", "Other"],
                    "Personal Care": ["Personal Grooming", "Fitness"],
                    "Leisure and Activities in Real Life": ["Movies", "Concerts"],
                    "Online Subscriptions & Services": ["Streaming & Digital Subscriptions", "Cloud Server Payments"]
                }
                
                # Generate the historical report using the ReportRepository


                

                historical_data = report_repository.create_historical_report(
                    user_id=user_id,
                    bank_account_id=bank_account_id,
                    start_date_filter=start_date, 
                    end_date_filter=end_date, 
                    master_category_list=master_category_list
                )



                # historical_data = report_repository.create_historical_report(
                #     user_id=user_id,
                #     bank_account_id=bank_account_id,
                #     master_category_list=master_category_list
                # )

                self.preprocessed_data = historical_data

                # Commit the session if necessary
                self.budget_tracker_session.commit()

            except HTTPException as http_exc:
                self.budget_tracker_session.rollback()
                logger.error(f"HTTPException during historical report generation: {http_exc.detail}")
                raise http_exc

            except Exception as e:
                self.budget_tracker_session.rollback()
                logger.error(f"An error occurred during historical report generation: {e}\n{format_exc()}")
                raise HTTPException(status_code=500, detail="Internal server error")

            finally:
                self.budget_tracker_session.close()

        except HTTPException as http_exc:
            # Re-raise HTTP exceptions to be handled by FastAPI
            raise http_exc

        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}\n{format_exc()}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def process_request(self):
        # Ensure the preprocessed data is in the format of the HistoricalAggregation model
        historical_aggregations = []
        for record in self.preprocessed_data:
            category_aggregations = [
                CategoryAggregation(**category) for category in record["category_aggregations"]
            ]
            historical_aggregations.append(
                HistoricalAggregation(
                    month=record["month"],
                    category_aggregations=category_aggregations,
                    total_income=record["total_income"],
                    total_spending=record["total_spending"]
                )
            )

        # Set the response as a list of HistoricalAggregation models
        self.response = historical_aggregations
