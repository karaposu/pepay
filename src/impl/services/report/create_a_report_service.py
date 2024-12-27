# impl/services/report/create_a_report_service.py

import logging
from fastapi import HTTPException
from traceback import format_exc
import os


logger = logging.getLogger(__name__)

class CreateAReportService:
    def __init__(self, request, dependencies):
        self.request = request
        self.dependencies = dependencies
        self.response = None
        self.currency_configs = dependencies.currency_configs()

        logger.debug("Inside CreateAReportService")

        self.preprocess_request_data()
        self.process_request()


    def preprocess_request_data(self):
        logger.debug("Inside preprocess_request_data")

        try:
            # Extract parameters from request
            user_id = self.request.user_id
            bank_account_id = self.request.bank_account_id
            start_date = self.request.start_date
            end_date = self.request.end_date
            currency = self.request.currency

            logger.debug(f"user_id: {user_id}")
            logger.debug(f"bank_account_id: {bank_account_id}")
            logger.debug(f"start_date: {start_date}")
            logger.debug(f"end_date: {end_date}")

            # Access session_factory and report_repository from dependencies
            logger.debug("Accessing session_factory and report_repository from dependencies")
            session_factory = self.dependencies.session_factory  # Should be a Singleton provider
            user_repository_provider = self.dependencies.user_repository
            report_repository_provider = self.dependencies.report_repository

            # Correctly obtain the sessionmaker and session instances
            sessionmaker_instance = session_factory()  # This gives us the sessionmaker
            session = sessionmaker_instance()  # This gives us the session

      
            try:
                logger.debug("Now inside the database session")

                # Instantiate the ReportRepository with the session
                user_repository = user_repository_provider(session=session)
                # report_repository = report_repository_provider(session=session)
                report_repository = report_repository_provider(
                    session=session,
                    currency_configs=self.currency_configs,
                    user_repository=user_repository
                )


                logger.debug("report_repository created")
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

                # Generate the report using the ReportRepository
                report = report_repository.create_a_report(
                    user_id=user_id,
                    bank_account_id=bank_account_id,
                    start_date=start_date,
                    end_date=end_date,
                    master_category_list=master_category_list,
                    currency= currency
                )

                self.preprocessed_data = report

                # Commit the session if necessary
                session.commit()

            except HTTPException as http_exc:
                session.rollback()
                logger.error(f"HTTPException during report generation: {http_exc.detail}")
                raise http_exc

            except Exception as e:
                session.rollback()
                logger.error(f"An error occurred during report generation: {e}\n{format_exc()}")
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