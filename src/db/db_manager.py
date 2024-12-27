# # here is db_manager.py
#
# import os
# import pandas as pd
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.exc import SQLAlchemyError
# from contextlib import contextmanager
# from io import StringIO
# from datetime import datetime
# from fastapi import HTTPException
# # from db_definitions import InitialData, ProcessedData, User
# # from db.db_models import InitialData, ProcessedData, User, FamilyGroup, UserFamilyGroup
#
# from db.models import InitialData, ProcessedData, User, FamilyGroup, UserFamilyGroup
#
# import logging
# from models.get_categorization_status200_response import GetCategorizationStatus200Response
# from models.get_my_files200_response_inner import GetMyFiles200ResponseInner
# from typing import List
# from models.split_record_dto import SplitRecordDTO
# from sqlalchemy import func
# import requests
# from db.models.exchange_db_definition import HistoricalCurrencyRates
# from models.selected_period_aggregation import SelectedPeriodAggregation
# from google.cloud.sql.connector import Connector, IPTypes
# from dotenv import load_dotenv
#
# logger = logging.getLogger(__name__)
#
# # Load environment variables
# load_dotenv()
#
# from dataclasses import dataclass
# @dataclass
# class IncomeAndSpending:
#     no_data_flag: bool
#     total_income: float
#     total_income_in_usd: float
#     total_income_in_gold: float
#     total_income_in_chf: float
#     total_spending: float
#     total_spending_in_usd: float
#     total_spending_in_gold: float
#     total_spending_in_chf: float
#
#
# @dataclass
# class SubcategoryAggregation:
#     name: str
#     total_amount: float
#     total_in_dollar: float
#     total_in_gold: float
#     total_in_chf: float
#
# @dataclass
# class CategoryAggregation:
#     category_name: str
#     total: float
#     total_in_dollar: float
#     total_in_gold: float
#     total_in_chf: float
#     subcategories: List[SubcategoryAggregation]
#
#
# def get_current_time():
#     return datetime.now()
#
#
# class DBManager:
#     def __init__(self, primary_db_path=None, secondary_db_path=None, logger=None):
#         self.logger = logger if logger else logging.getLogger('db_manager')
#
#         # Determine whether to use Cloud SQL or local SQLite
#         use_cloud_sql = os.getenv('USE_CLOUD_SQL', 'False').lower() == 'true'
#
#         if use_cloud_sql:
#             self.logger.info("Using Cloud SQL for the primary database.")
#             self.primary_engine = self.create_cloud_sql_engine(db_name=os.getenv('DB_NAME'))
#         else:
#             self.logger.info("Using local SQLite for the primary database.")
#             if not primary_db_path:
#                 raise ValueError("Primary DB path must be provided when not using Cloud SQL.")
#             self.primary_engine = create_engine(f'sqlite:///{primary_db_path}')
#
#         self.PrimarySession = sessionmaker(bind=self.primary_engine)
#
#         # Set up the secondary database (e.g., for exchange rates)
#         if secondary_db_path:
#             self.logger.info("Using local SQLite for the secondary database.")
#             self.secondary_engine = create_engine(f'sqlite:///{secondary_db_path}')
#             self.SecondarySession = sessionmaker(bind=self.secondary_engine)
#         else:
#             self.secondary_engine = None
#             self.SecondarySession = None
#
#     def create_cloud_sql_engine(self, db_name):
#         """
#         Creates a SQLAlchemy engine connected to the Cloud SQL instance.
#         """
#         instance_connection_name = os.environ.get("INSTANCE_CONNECTION_NAME")
#         db_user = os.environ.get("DB_USER")
#         db_pass = os.environ.get("DB_PASS")
#         ip_type = IPTypes.PUBLIC  # or IPTypes.PRIVATE depending on your setup
#
#         if not all([instance_connection_name, db_user, db_pass, db_name]):
#             self.logger.error("Missing required environment variables for Cloud SQL connection.")
#             raise ValueError("Missing required environment variables for Cloud SQL connection.")
#
#         connector = Connector()
#
#         def getconn():
#             conn = connector.connect(
#                 instance_connection_name,
#                 "pymysql",
#                 user=db_user,
#                 password=db_pass,
#                 db=db_name,
#                 ip_type=ip_type
#             )
#             return conn
#
#         engine = create_engine(
#             "mysql+pymysql://",
#             creator=getconn,
#             pool_recycle=3600,
#         )
#         return engine
#
#     @contextmanager
#     def session_scope(self):
#         session = self.PrimarySession()
#         try:
#             yield session
#             session.commit()
#         except SQLAlchemyError as e:
#             session.rollback()
#             self.logger.error(f"Primary session rollback due to error: {e}")
#             raise
#         finally:
#             session.close()
#
#     @contextmanager
#     def secondary_session_scope(self):
#         if not self.secondary_engine:
#             raise RuntimeError("Secondary database is not configured.")
#         session = self.SecondarySession()
#         try:
#             yield session
#             session.commit()
#         except SQLAlchemyError as e:
#             session.rollback()
#             self.logger.error(f"Secondary session rollback due to error: {e}")
#             raise
#         finally:
#             session.close()
#
#     # @contextmanager
#     # def session_scope(self):
#     #     session = self.Session()
#     #     try:
#     #         yield session
#     #         session.commit()
#     #     except SQLAlchemyError as e:
#     #         session.rollback()
#     #         self.logger.error(f"Session rollback due to error: {e}")
#     #         raise HTTPException(status_code=500, detail="Internal server error")
#     #     finally:
#     #         session.close()
#
#     def advanced_log_progress(self, current_record, total_records, user_id, file_id, elapsed_time_in_seconds=None,
#                               log_every_n=10):
#
#         if (current_record + 1) % log_every_n == 0 or current_record + 1 == total_records:
#             # Calculate progress percentage
#             progress = (current_record + 1) / total_records
#
#             # Calculate remaining time if elapsed_time is provided
#             remaining_time_seconds = None
#             formatted_time = None
#             if elapsed_time_in_seconds and progress > 0:
#                 self.logger.error(f"elapsed_time_in_seconds: {elapsed_time_in_seconds}")
#                 remaining_time_seconds = elapsed_time_in_seconds / progress * (1 - progress)
#                 self.logger.error(f"remaining_time_seconds: {remaining_time_seconds}")
#
#                 remaining_time_seconds = int(remaining_time_seconds)
#
#                 minutes, seconds = divmod(remaining_time_seconds, 60)
#                 formatted_time = f"{int(minutes)}:{int(seconds):02d}"
#
#                 # remaining_time_minutes = remaining_time_seconds / 60
#
#             # Call the original log_progress method with the calculated remaining time
#             self.log_progress(current_record, total_records, user_id, file_id, remaining_time_seconds, formatted_time)
#
#
#     def revert_split(self, record_id: int):
#         with self.session_scope() as session:
#             try:
#                 # Retrieve the original record by record_id
#                 original_record = session.query(ProcessedData).filter_by(record_id=record_id).first()
#
#                 if not original_record:
#                     self.logger.error(f"Original record with record_id {record_id} not found.")
#                     raise HTTPException(status_code=404, detail="Original record not found")
#
#                 # Find all split records associated with the original record
#                 split_records = session.query(ProcessedData).filter_by(parent_record_id=record_id).all()
#
#                 if not split_records:
#                     self.logger.warning(f"No split records found for original record_id {record_id}.")
#                     raise HTTPException(status_code=404, detail="No split records found")
#
#                 # Deactivate all split records
#                 for record in split_records:
#                     record.is_active = False
#                     session.add(record)
#
#                 # Reactivate the original record
#                 original_record.is_active = True
#                 original_record.is_split = False
#                 session.add(original_record)
#
#                 # Commit the transaction
#                 session.commit()
#                 self.logger.info(f"Reverted split for record_id {record_id} successfully.")
#
#             except Exception as e:
#                 session.rollback()
#                 self.logger.error(f"Error reverting split for record_id {record_id}: {str(e)}")
#                 raise HTTPException(status_code=500, detail="Error reverting split")
#
#     def list_files(self, user_id, bank_name) -> List[GetMyFiles200ResponseInner]:
#         """
#         List all files in the InitialData table, optionally filtered by user ID.
#
#         :param user_id: ID of the user to filter files by. If None, all files are returned.
#         :return: List of GetMyFiles200ResponseInner instances.
#         """
#         with self.session_scope() as session:
#             query = session.query(InitialData)
#
#             if user_id is not None:
#                 query = query.filter(InitialData.user_id == user_id)
#
#             files = query.all()
#
#             # Create a list of GetMyFiles200ResponseInner instances to represent each file
#             file_list = []
#             for file in files:
#                 file_list.append(
#                     GetMyFiles200ResponseInner(
#                         document_id=file.document_id,
#                         associated_with=file.associated_with,
#                         bank_account_alias=file.bank_account_alias,
#                         bank_account_id=file.bank_account_id,
#                         remaining_time_estimation=file.remaining_time_estimation,
#                         process_status_in_percentage=file.process_status_in_percentage,
#                         process_status=file.process_status,
#                         number_of_records=file.number_of_records,
#                         num_processed_records=session.query(ProcessedData).filter_by(
#                             document_id=file.document_id).count(),
#                         upload_timestamp=file.upload_timestamp,
#                         start_date=file.start_date,
#                         end_date=file.end_date
#                     )
#                 )
#
#             return file_list
#
#     def split_record(self, record_id: int, splits: List[SplitRecordDTO]):
#         with self.session_scope() as session:
#             try:
#                 original_record = session.query(ProcessedData).filter_by(record_id=record_id).first()
#
#                 if not original_record:
#                     self.logger.error(f"Original record with record_id {record_id} not found.")
#                     raise HTTPException(status_code=404, detail="Original record not found")
#
#                 # Deactivate the original record
#                 original_record.is_active = False
#                 original_record.is_split = True
#                 session.add(original_record)
#
#                 # Create split records
#                 for split_data in splits:
#                     if not isinstance(split_data, SplitRecordDTO):
#                         self.logger.error(f"Expected SplitRecordDTO, got {type(split_data)}")
#                         raise HTTPException(status_code=400, detail="Invalid split data format")
#
#                     split_record = ProcessedData(
#                         user_id=original_record.user_id,
#                         document_id=original_record.document_id,
#                         text=split_data.text,
#                         cleaned_text=split_data.text,  # Adjust if needed
#                         amount=split_data.amount,
#                         category=split_data.category,
#                         subcategory=split_data.subcategory,
#                         rationale="",
#                         refiner_output="",
#                         categorized_by="user",
#                         record_date=get_current_time(),
#                         associated_with=original_record.associated_with,
#                         parent_record_id=original_record.record_id,
#                         split_level=original_record.split_level + 1,
#                         is_active=True  # New split records should be active
#                     )
#                     session.add(split_record)
#
#                 # Commit the transaction
#                 session.commit()
#                 self.logger.info(
#                     f"Record with record_id {original_record.record_id} split successfully into {len(splits)} records.")
#
#             except Exception as e:
#                 session.rollback()
#                 self.logger.error(f"Error splitting record with record_id {record_id}: {str(e)}")
#                 raise HTTPException(status_code=500, detail="Error splitting record")
#
#     def merge_splits(self, original_record_id: int):
#         with self.session_scope() as session:
#             try:
#                 # Find the original record
#                 original_record = session.query(ProcessedData).filter_by(record_id=original_record_id).first()
#
#                 if not original_record:
#                     self.logger.error(f"Original record with id {original_record_id} not found.")
#                     raise HTTPException(status_code=404, detail="Original record not found")
#
#                 # Find all active split records associated with the original record
#                 split_records = session.query(ProcessedData).filter_by(parent_record_id=original_record_id,
#                                                                        is_active=True).all()
#
#                 if not split_records:
#                     self.logger.error(f"No active split records found for original record id {original_record_id}.")
#                     raise HTTPException(status_code=404, detail="No active split records found")
#
#                 # Reactivate the original record and deactivate all active split records
#                 original_record.is_active = True
#                 original_record.is_split = False
#                 session.add(original_record)
#
#                 for split_record in split_records:
#                     split_record.is_active = False
#                     session.add(split_record)
#
#                 # Commit the transaction
#                 session.commit()
#                 self.logger.info(
#                     f"Record with record_id {original_record_id} merged successfully from {len(split_records)} split records.")
#
#             except Exception as e:
#                 session.rollback()
#                 self.logger.error(f"Error merging record with record_id {original_record_id}: {str(e)}")
#                 raise HTTPException(status_code=500, detail="Error merging records")
#
#
#     # this is from oldd db_manager.py
#     def create_historical_report(self, user_id, bank_account_id, master_category_list):
#         with self.session_scope() as session:
#             # Group the records by month and aggregate income and spending
#             self.logger.debug(f"Creating historical report for user_id: {user_id}, bank_account_id: {bank_account_id}")
#
#             query = session.query(func.strftime('%Y-%m', ProcessedData.record_date).label('month')).filter(
#                 ProcessedData.user_id == user_id)
#
#             if bank_account_id is not None:
#                 query = query.filter(ProcessedData.document_id == bank_account_id)
#
#             months = query.group_by(func.strftime('%Y-%m', ProcessedData.record_date)).all()
#
#             self.logger.debug(f"Found months: {months}")
#
#             historical_aggregations = []
#
#             for month, in months:
#                 self.logger.debug(f"Processing month: {month}")
#
#                 # Get start_date and end_date for the month
#                 start_date = f"{month}-01"
#                 end_date = f"{month}-{self.get_last_day_of_month(month)}"
#                 self.logger.debug(f"Start date: {start_date}, End date: {end_date}")
#
#                 # Aggregate income and spending for the month
#                 total_income, total_spending = self.aggregate_income_and_spending(
#                     session, user_id, bank_account_id, start_date, end_date
#                 )
#                 self.logger.debug(f"Total income: {total_income}, Total spending: {total_spending}")
#
#                 # Aggregate categories and subcategories for the month
#                 category_aggregations = self.aggregate_categories_and_subcategories(
#                     session, user_id, bank_account_id, start_date, end_date, master_category_list
#                 )
#                 self.logger.debug(f"Category aggregations for {month}: {category_aggregations}")
#
#                 # Add to historical aggregations
#                 historical_aggregations.append({
#                     "month": month,
#                     "category_aggregations": category_aggregations,
#                     "total_income": total_income,
#                     "total_spending": total_spending
#                 })
#
#             self.logger.debug(f"Final historical aggregations: {historical_aggregations}")
#             return historical_aggregations
#
#     def get_last_day_of_month(self, month):
#         import calendar
#         # Helper method to get the last day of a month in YYYY-MM format
#         year, month = map(int, month.split('-'))
#         return calendar.monthrange(year, month)[1]
#
#     def aggregate_income_and_spending(self, session, user_id, bank_account_id, start_date, end_date):
#         # Helper function to conditionally apply the bank_account_id filter
#         def apply_bank_account_filter(query):
#             if bank_account_id is not None:
#                 return query.filter(ProcessedData.document_id == bank_account_id)
#             return query
#
#         data_exists = apply_bank_account_filter(
#             session.query(ProcessedData.id)
#             .filter(
#                 ProcessedData.user_id == user_id,
#                 ProcessedData.record_date >= start_date,
#                 ProcessedData.record_date <= end_date,
#             )
#         ).first() is not None
#
#         if not data_exists:
#             return IncomeAndSpending(
#                 no_data_flag=True,
#                 total_income=0,
#                 total_income_in_usd=0,
#                 total_income_in_gold=0,
#                 total_income_in_chf=0,
#                 total_spending=0,
#                 total_spending_in_usd=0,
#                 total_spending_in_gold=0,
#                 total_spending_in_chf=0
#             )
#
#         # Calculate total income in base currency, USD, Gold, and CHF
#         total_income = apply_bank_account_filter(
#             session.query(func.sum(ProcessedData.amount))
#             .filter(
#                 ProcessedData.user_id == user_id,
#                 ProcessedData.record_date >= start_date,
#                 ProcessedData.record_date <= end_date,
#                 ProcessedData.amount > 0  # Considering positive amounts as income
#             )
#         ).scalar() or 0
#
#         total_income_in_usd = apply_bank_account_filter(
#             session.query(func.sum(ProcessedData.amount_in_dollar))
#             .filter(
#                 ProcessedData.user_id == user_id,
#                 ProcessedData.record_date >= start_date,
#                 ProcessedData.record_date <= end_date,
#                 ProcessedData.amount > 0  # Considering positive amounts as income
#             )
#         ).scalar() or 0
#
#         total_income_in_gold = apply_bank_account_filter(
#             session.query(func.sum(ProcessedData.amount_in_gold))
#             .filter(
#                 ProcessedData.user_id == user_id,
#                 ProcessedData.record_date >= start_date,
#                 ProcessedData.record_date <= end_date,
#                 ProcessedData.amount > 0  # Considering positive amounts as income
#             )
#         ).scalar() or 0
#
#         total_income_in_chf = apply_bank_account_filter(
#             session.query(func.sum(ProcessedData.amount_in_chf))
#             .filter(
#                 ProcessedData.user_id == user_id,
#                 ProcessedData.record_date >= start_date,
#                 ProcessedData.record_date <= end_date,
#                 ProcessedData.amount > 0  # Considering positive amounts as income
#             )
#         ).scalar() or 0
#
#         # Calculate total spending in base currency, USD, Gold, and CHF
#         total_spending = apply_bank_account_filter(
#             session.query(func.sum(ProcessedData.amount))
#             .filter(
#                 ProcessedData.user_id == user_id,
#                 ProcessedData.record_date >= start_date,
#                 ProcessedData.record_date <= end_date,
#                 ProcessedData.amount < 0  # Considering negative amounts as spending
#             )
#         ).scalar() or 0
#
#         total_spending_in_usd = apply_bank_account_filter(
#             session.query(func.sum(ProcessedData.amount_in_dollar))
#             .filter(
#                 ProcessedData.user_id == user_id,
#                 ProcessedData.record_date >= start_date,
#                 ProcessedData.record_date <= end_date,
#                 ProcessedData.amount < 0  # Considering negative amounts as spending
#             )
#         ).scalar() or 0
#
#         total_spending_in_gold = apply_bank_account_filter(
#             session.query(func.sum(ProcessedData.amount_in_gold))
#             .filter(
#                 ProcessedData.user_id == user_id,
#                 ProcessedData.record_date >= start_date,
#                 ProcessedData.record_date <= end_date,
#                 ProcessedData.amount < 0  # Considering negative amounts as spending
#             )
#         ).scalar() or 0
#
#         total_spending_in_chf = apply_bank_account_filter(
#             session.query(func.sum(ProcessedData.amount_in_chf))
#             .filter(
#                 ProcessedData.user_id == user_id,
#                 ProcessedData.record_date >= start_date,
#                 ProcessedData.record_date <= end_date,
#                 ProcessedData.amount < 0  # Considering negative amounts as spending
#             )
#         ).scalar() or 0
#
#         return IncomeAndSpending(
#             no_data_flag=False,
#             total_income=total_income,
#             total_income_in_usd=total_income_in_usd,
#             total_income_in_gold=total_income_in_gold,
#             total_income_in_chf=total_income_in_chf,
#             total_spending=total_spending,
#             total_spending_in_usd=total_spending_in_usd,
#             total_spending_in_gold=total_spending_in_gold,
#             total_spending_in_chf=total_spending_in_chf
#         )
#
#
#     def aggregate_and_format_categories(self, queried_data, master_category_list):
#         self.logger.debug(f"Aggregating and formatting categories from queried data.")
#
#         # Organizing the results into categories and subcategories
#         category_dict = {
#             category: {
#                 "total": 0,
#                 "total_in_dollar": 0,
#                 "total_in_gold": 0,
#                 "total_in_chf": 0,
#                 "subcategories": []
#             } for category in master_category_list
#         }
#
#         for category, subcategory, total, total_in_dollar, total_in_gold, total_in_chf in queried_data:
#             self.logger.debug(f"Processing category: {category}, subcategory: {subcategory}, total: {total}")
#             if category in category_dict:
#                 if subcategory in master_category_list[category]:
#                     category_dict[category]["total"] += total
#                     category_dict[category]["total_in_dollar"] += total_in_dollar
#                     category_dict[category]["total_in_gold"] += total_in_gold
#                     category_dict[category]["total_in_chf"] += total_in_chf
#                     category_dict[category]["subcategories"].append({
#                         "name": subcategory,
#                         "total_amount": total,
#                         "total_in_dollar": total_in_dollar,
#                         "total_in_gold": total_in_gold,
#                         "total_in_chf": total_in_chf
#                     })
#
#         self.logger.debug(f"Category dictionary before formatting: {category_dict}")
#
#         # Formatting the result
#         category_aggregations = []
#         for category_name, data in category_dict.items():
#             if data["total"] != 0:  # Capture all non-zero categories
#                 # subcategories = [
#                 #     SubcategoryAggregation(
#                 #         name=sub["name"],
#                 #         total_amount=sub["total_amount"],
#                 #         total_in_dollar=sub["total_in_dollar"],
#                 #         total_in_gold=sub["total_in_gold"],
#                 #         total_in_chf=sub["total_in_chf"]
#                 #     ) for sub in data["subcategories"]
#                 # ]
#                 # category_aggregations.append(
#                 #     CategoryAggregation(
#                 #         category_name=category_name,
#                 #         total=data["total"],
#                 #         total_in_dollar=data["total_in_dollar"],
#                 #         total_in_gold=data["total_in_gold"],
#                 #         total_in_chf=data["total_in_chf"],
#                 #         subcategories=subcategories
#                 #     )
#                 # )
#
#                 category_aggregations.append({
#                     "category_name": category_name,
#                     "total": data["total"],
#                     "total_in_dollar": data["total_in_dollar"],
#                     "total_in_gold": data["total_in_gold"],
#                     "total_in_chf": data["total_in_chf"],
#                     "subcategories": data["subcategories"]
#                 })
#
#         self.logger.debug(f"Final category aggregations: {category_aggregations}")
#         return category_aggregations
#
#     def query_category_totals(self, session, user_id, bank_account_id, start_date, end_date):
#         self.logger.debug(
#             f"Querying category totals for user_id: {user_id}, bank_account_id: {bank_account_id}, start_date: {start_date}, end_date: {end_date}")
#
#         # Query to fetch categories and subcategories within the selected period
#         query = session.query(
#             ProcessedData.category,
#             ProcessedData.subcategory,
#             func.sum(ProcessedData.amount).label('total_amount'),
#             func.sum(ProcessedData.amount_in_dollar).label('total_amount_in_dollar'),
#             func.sum(ProcessedData.amount_in_gold).label('total_amount_in_gold'),
#             func.sum(ProcessedData.amount_in_chf).label('total_amount_in_chf')
#         ).filter(
#             ProcessedData.user_id == user_id,
#             ProcessedData.record_date >= start_date,
#             ProcessedData.record_date <= end_date
#         )
#
#         if bank_account_id is not None:
#             query = query.filter(ProcessedData.document_id == bank_account_id)
#
#         results = query.group_by(
#             ProcessedData.category,
#             ProcessedData.subcategory
#         ).all()
#
#         # self.logger.debug(f"Queried categories: {results}")
#         return results
#
#     def aggregate_categories_and_subcategories(self, session, user_id, bank_account_id, start_date, end_date,
#                                                master_category_list):
#         # Part 1: Query the category totals
#         queried_data = self.query_category_totals(session, user_id, bank_account_id, start_date, end_date)
#
#         # Part 2: Aggregate and format the results
#         category_aggregations = self.aggregate_and_format_categories(queried_data, master_category_list)
#
#         return category_aggregations
#
#
#     # this is from old db_manager.py
#     def create_a_report(self, user_id, bank_account_id, start_date, end_date, master_category_list):
#         with self.session_scope() as session:
#
#             # user should have default currency. and it should be shown
#
#             income_and_spending = self.aggregate_income_and_spending(session, user_id, bank_account_id, start_date,
#                                                                      end_date)
#
#             if income_and_spending.no_data_flag:
#                 report = SelectedPeriodAggregation(
#                     # category_aggregations=[],
#                     total_income=0,
#                     total_income_currency="TRY",  # Replace with actual currency code
#                     total_spending=0,
#                     total_spending_currency="TRY",  # Replace with actual currency code
#                     total_income_in_dollar=0,
#                     total_income_in_gold=0,
#                     total_income_in_chf=0,
#                     total_spending_in_dollar=0,
#                     total_spending_in_gold=0,
#                     total_spending_in_chf=0
#                 )
#                 return report
#
#             currency_code = session.query(ProcessedData.currency).filter(
#                 ProcessedData.user_id == user_id,
#                 ProcessedData.bank_account_id == bank_account_id
#             ).first()
#
#             # currency_code = currency_code[0] if currency_code else "USD"
#             if currency_code is not None:
#                 currency_code = currency_code[0]
#             else:
#                 "TRY"
#
#             # currency_code = self.get_currency_code_for_user(user_id)
#
#             # Aggregate categories and subcategories
#             category_aggregations = self.aggregate_categories_and_subcategories(
#                 session, user_id, bank_account_id, start_date, end_date, master_category_list
#             )
#
#
#             report = SelectedPeriodAggregation(
#                 category_aggregations=category_aggregations,
#                 total_income=income_and_spending.total_income,
#                 total_income_currency=currency_code,
#                 total_spending=income_and_spending.total_spending,
#                 total_spending_currency=currency_code,
#                 total_income_in_dollar=income_and_spending.total_income_in_usd,
#                 total_income_in_gold=income_and_spending.total_income_in_gold,
#                 total_income_in_chf=income_and_spending.total_income_in_chf,
#                 total_spending_in_dollar=income_and_spending.total_spending_in_usd,
#                 total_spending_in_gold=income_and_spending.total_spending_in_gold,
#                 total_spending_in_chf=income_and_spending.total_spending_in_chf
#             )
#
#             return report
#
#
#     def get_bank_information(self, country=None, supported=None):
#         import json
#         from db.models.info_db_definitions import BankInformation
#         with self.session_scope() as session:
#             # Start the base query for BankInformation
#             query = session.query(BankInformation)
#
#             # Apply filters dynamically based on provided parameters
#             if country:
#                 query = query.filter(BankInformation.country == country)
#
#             if supported is not None:  # Check if supported is explicitly set to True or False
#                 query = query.filter(BankInformation.supported == supported)
#
#             # Fetch the results
#             results = query.all()
#
#             # Return a list of dictionaries representing the results
#             return [{
#                 'name': bank.name,
#                 'country': bank.country,
#                 'id': bank.id,
#                 'supported': bank.supported,
#                 'aliases': json.loads(bank.aliases) if bank.aliases else [],
#                 'supported_file_formats': json.loads(
#                     bank.supported_file_formats) if bank.supported_file_formats else [],
#                 'notes': bank.notes,
#                 'info': bank.info,
#                 'logo': bank.logo,
#                 'illustration': bank.illustration,
#                 'website_url': bank.website_url,
#                 'customer_support_number': bank.customer_support_number,
#                 'established_date': bank.established_date,
#                 'available_services': bank.available_services,
#                 'currency_code': bank.currency_code,
#                 'is_international': bank.is_international,
#                 'tier': bank.tier,
#             } for bank in results]
#
#     def update_processed_data(self, df: pd.DataFrame):
#         with self.session_scope() as session:
#             try:
#                 for _, row in df.iterrows():
#                     # Retrieve the existing record by record_id
#                     record_id = row.get('record_id')
#                     if record_id is None:
#                         self.logger.warning("Record ID not found in the data frame row. Skipping update.")
#                         continue
#
#                     existing_record = session.query(ProcessedData).filter_by(record_id=record_id).first()
#
#                     if existing_record:
#                         # Update the existing record's fields
#                         existing_record.amount = row.get('amount', existing_record.amount)
#                         existing_record.rationale = row.get('rationale', existing_record.rationale)
#                         existing_record.refiner_output = row.get('refiner_output', existing_record.refiner_output)
#
#                         #
#                         # existing_record.categorization_result = row.get('category_dict', {}).get('category',   existing_record.categorization_result)
#                         # existing_record.category = row.get('category_dict', {}).get('lvl1', existing_record.category)
#                         # existing_record.subcategory = row.get('category_dict', {}).get('lvl2',existing_record.subcategory)
#
#                         existing_record.category = row.get('lvl1', existing_record.category)
#                         existing_record.subcategory = row.get('lvl2', existing_record.subcategory)
#
#                         existing_record.categorized_by = row.get('categorized_by', existing_record.categorized_by)
#                         #  existing_record.record_date = get_current_time()  # Assuming current time for simplicity
#                         existing_record.associated_with = row.get('associated_with', existing_record.associated_with)
#
#                         existing_record.matched_auto_trigger_keyword = row.get('matched_auto_trigger_keyword',
#                                                                                existing_record.matched_auto_trigger_keyword)
#                         existing_record.matched_metapattern = row.get('matched_metapattern',
#                                                                       existing_record.matched_metapattern)
#
#                         # Mark the record as dirty to trigger an update
#                         session.add(existing_record)
#                     else:
#                         # If no existing record is found, log a warning and skip the update
#                         self.logger.warning(f"Record not found for record_id {record_id}. Skipping update.")
#                         continue
#
#                 # Commit the transaction
#                 session.commit()
#                 self.logger.info("ProcessedData table updated successfully.")
#
#             except Exception as e:
#                 session.rollback()
#                 self.logger.error(f"Error updating ProcessedData: {str(e)}")
#                 raise HTTPException(status_code=500, detail="Error updating processed data")
#
#
#
#     def update_processing_status(self, user_id: int, file_id: int, status: str = None, percentage: int = None,
#                                  started_at: datetime = None, completed_at: datetime = None,
#                                  remaining_time: str = None):
#         with self.session_scope() as session:
#             # Retrieve the row by user_id and file_id
#
#             # self.logger.error("--------rrr")
#
#             selected_file_row = session.query(InitialData).filter_by(user_id=user_id, document_id=file_id).first()
#
#             if selected_file_row:
#                 # Update the process status and other columns if provided
#                 if status is not None:
#                     selected_file_row.process_status = status
#                 if percentage is not None:
#                     selected_file_row.process_status_in_percentage = percentage
#                 if started_at is not None:
#                     selected_file_row.process_started_at = started_at
#                 if completed_at is not None:
#                     selected_file_row.process_completed_at = completed_at
#                 if remaining_time is not None:
#                     selected_file_row.remaining_time_estimation = remaining_time
#
#                 # Commit the changes
#                 session.add(selected_file_row)
#                 self.logger.info(f"         Updated processing status for file_id {file_id} to {status}")
#
#             else:
#                 self.logger.error(f"File with id {file_id} for user {user_id} not found")
#                 raise HTTPException(status_code=404, detail="File not found")
#
#     def make_user_verified_from_email(self, email):
#         with self.session_scope() as session:
#             db_user = self.get_user_by_email(session, email)
#             if db_user:
#                 db_user.is_verified = True
#                 session.add(db_user)
#
#     def get_user_by_email(self, session, email):
#         try:
#             db_user = session.query(User).filter(User.email == email).first()
#             if not db_user:
#                 return None
#             return db_user
#         except SQLAlchemyError as e:
#             session.rollback()
#             self.logger.error(f"Database error: {e}")
#             return None
#
#     def add_new_user(self, email, hashed_password):
#         with self.session_scope() as session:
#             try:
#                 db_user = User(
#                     email=email,
#                     password_hash=hashed_password,
#                     created_at=get_current_time(),
#                     name="p"  # You can set the name dynamically if needed
#                 )
#                 session.add(db_user)
#                 session.commit()  # Commit the transaction to save the user and generate the user_id
#
#                 # Return the newly created user's ID
#                 return db_user.user_id
#             except SQLAlchemyError as e:
#                 session.rollback()  # Rollback the transaction in case of an error
#                 self.logger.error(f"Error adding new user: {str(e)}")
#                 raise HTTPException(status_code=500, detail="Error adding new user")
#
#     def check_user_by_email(self, email):
#         with self.session_scope() as session:
#             db_user = session.query(User).filter(User.email == email).first()
#             if db_user:
#                 raise HTTPException(status_code=400, detail="Email already registered")
#             return db_user
#
#     def login(self, email, new_password):
#         with self.session_scope() as session:
#             user = self.get_user_by_email(session, email)
#             if not user:
#                 raise HTTPException(status_code=400, detail="User not found")
#             user.password_hash = self.pwd_context.hash(new_password)
#             session.add(user)
#
#     def hash_password(self, password):
#         return self.pwd_context.hash(password)
#
#     def change_password(self, email, new_password):
#         with self.session_scope() as session:
#             # Retrieve the user by email
#             user = self.get_user_by_email(session, email)
#             if not user:
#                 raise HTTPException(status_code=400, detail="User not found")
#
#             # Log the old hashed password
#             old_hashed_password = user.password_hash
#             self.logger.debug(f"Old hashed password for {email}: {old_hashed_password}")
#
#             # Hash the new password and log it
#             new_hashed_password = self.pwd_context.hash(new_password)
#             self.logger.debug(f"New hashed password for {email}: {new_hashed_password}")
#
#             # Update the user's password
#             user.password_hash = new_hashed_password
#             session.add(user)
#             session.commit()
#
#             # Retrieve the updated user from the database
#             updated_user = self.get_user_by_email(session, email)
#
#             # Log the updated hashed password from the database
#             self.logger.debug(f"Updated hashed password for {email} in DB: {updated_user.password_hash}")
#
#             session.refresh(user)
#             updated_user = self.get_user_by_email(session, email)
#             self.logger.debug(
#                 f" After Refresh Updated Password hash for {email} after refresh: {updated_user.password_hash}")
#
#             # Verify the new password against the updated hash
#             if not self.pwd_context.verify(new_password, updated_user.password_hash):
#                 self.logger.error(f"Failed to update the password for {email}.")
#                 raise HTTPException(status_code=500, detail="Failed to update the password.")
#             else:
#                 self.logger.debug(f"Password for {email} successfully updated in the database.")
#
#     def get_file_by_user_and_file_id(self, user_id, file_id):
#         with self.session_scope() as session:
#             selected_file_row = session.query(InitialData).filter_by(user_id=user_id, document_id=file_id).all()
#
#             return selected_file_row
#
#     def should_log_progress(self, number_of_processed_records, total_records, n=1):
#
#         return (number_of_processed_records % n == 0) or (number_of_processed_records == total_records)
#
#     def log_progress(self, current_record, total_records, progress_percentage, remaining_time_seconds,
#                      remaining_time_str, user_id, file_id):
#         if self.should_log_progress(current_record, total_records):
#             # self.logger.info(
#             #     f"Processed {current_record}/{total_records} records ({progress_percentage:.2f}% complete), "
#             #     f"remaining time: {remaining_time_str}"
#             # )
#
#             with self.session_scope() as session:
#                 selected_file_row = session.query(InitialData).filter_by(user_id=user_id, document_id=file_id).first()
#
#                 if selected_file_row:
#                     selected_file_row.number_of_processed = current_record + 1
#                     selected_file_row.process_status_in_percentage = int(progress_percentage)
#                     if remaining_time_seconds is not None:
#                         selected_file_row.remaining_time_estimation = remaining_time_seconds  # Store remaining time in seconds
#                         selected_file_row.remaining_time_estimation_str = remaining_time_str  # Optionally store the formatted string
#                     session.add(selected_file_row)
#                 else:
#                     self.logger.error(f"File with id {file_id} for user {user_id} not found")
#                     raise HTTPException(status_code=404, detail="File not found")
#
#     # def log_progress(self, current_record, total_records, user_id, file_id, remaining_time=None, remaining_time_str=None):
#     #    # if (current_record + 1) % 10 == 0 or current_record + 1 == total_records:
#     #         process_status_in_percentage = (current_record + 1) / total_records * 100
#     #       #  self.logger.info(f"Processed {current_record + 1}/{total_records} records ({process_status_in_percentage:.2f}% complete), remaining time: {remaining_time:.2f} minutes")
#     #
#     #         with self.session_scope() as session:
#     #             selected_file_row = session.query(InitialData).filter_by(user_id=user_id, document_id=file_id).first()
#     #
#     #             if selected_file_row:
#     #                 selected_file_row.process_status_in_percentage = int(process_status_in_percentage)
#     #                 selected_file_row.number_of_processed = int(current_record) +1
#     #                 if remaining_time is not None:
#     #                    # selected_file_row.remaining_time_estimation = f"{int(remaining_time):02d}:{int((remaining_time * 60) % 60):02d}"
#     #                     selected_file_row.remaining_time_estimation = remaining_time
#     #                     selected_file_row.remaining_time_estimation_str = remaining_time_str
#     #
#     #                 session.add(selected_file_row)
#     #             else:
#     #                 self.logger.error(f"File with id {file_id} for user {user_id} not found")
#     #                 raise HTTPException(status_code=404, detail="File not found")
#
#     def delete_record(self, record_id: int):
#         with self.session_scope() as session:
#             try:
#                 # Retrieve the record by record_id
#                 record_to_delete = session.query(ProcessedData).filter_by(record_id=record_id).first()
#
#                 if record_to_delete:
#                     # Delete the record from the session
#                     session.delete(record_to_delete)
#                     self.logger.info(f"Record with record_id {record_id} deleted successfully.")
#                 else:
#                     self.logger.error(f"Record with record_id {record_id} not found.")
#                     raise HTTPException(status_code=404, detail="Record not found")
#
#             except Exception as e:
#                 session.rollback()
#                 self.logger.error(f"Error deleting record with record_id {record_id}: {str(e)}")
#                 raise HTTPException(status_code=500, detail="Error deleting record")
#
#     def get_records(self, user_id=None, document_id=None, start_date=None, end_date=None, associated_with=None):
#         with self.session_scope() as session:
#             # Start with the base query for ProcessedData
#             query = session.query(ProcessedData)
#
#             # Apply filters dynamically based on the provided arguments
#             if user_id is not None:
#                 query = query.filter(ProcessedData.user_id == user_id)
#             if document_id is not None:
#                 query = query.filter(ProcessedData.document_id == document_id)
#             if start_date is not None:
#                 query = query.filter(ProcessedData.record_date >= start_date)
#             if end_date is not None:
#                 query = query.filter(ProcessedData.record_date <= end_date)
#             if associated_with is not None:
#                 query = query.filter(ProcessedData.associated_with == associated_with)
#
#             # Execute the query and fetch all matching records
#             records = query.all()
#
#             # Extract column names from the ProcessedData model
#             column_names = ProcessedData.__table__.columns.keys()
#
#             # Create the data dictionary
#             data = [
#                 {column: getattr(record, column) for column in column_names}
#                 for record in records
#             ]
#
#             # Create the DataFrame
#             df = pd.DataFrame(data, columns=column_names)
#
#             return df
#
#     def get_records_with_pagination(self, user_id=None, document_id=None, start_date=None, end_date=None,
#                                     associated_with=None,
#                                     limit=30, offset=0):
#         with self.session_scope() as session:
#             # Start with the base query for ProcessedData
#             query = session.query(ProcessedData)
#
#             # Apply filters dynamically based on the provided arguments
#             if user_id is not None:
#                 query = query.filter(ProcessedData.user_id == user_id)
#             if document_id is not None:
#                 query = query.filter(ProcessedData.document_id == document_id)
#             if start_date is not None:
#                 query = query.filter(ProcessedData.record_date >= start_date)
#             if end_date is not None:
#                 query = query.filter(ProcessedData.record_date <= end_date)
#             if associated_with is not None:
#                 query = query.filter(ProcessedData.associated_with == associated_with)
#
#             # Get the total count before applying limit and offset
#             total = query.count()
#
#             # Apply limit and offset for pagination
#             query = query.limit(limit).offset(offset)
#
#             # Execute the query and fetch the records
#             records = query.all()
#
#             # Extract column names from the ProcessedData model
#             column_names = ProcessedData.__table__.columns.keys()
#
#             # Create the data dictionary
#             data = [
#                 {column: getattr(record, column) for column in column_names}
#                 for record in records
#             ]
#
#             # Create the DataFrame
#             df = pd.DataFrame(data, columns=column_names)
#
#             # Return both the DataFrame and the total count
#             return df, total
#
#     # def get_records_with_pagination(self, user_id=None, document_id=None, start_date=None, end_date=None, associated_with=None,
#     #                  limit=30, offset=0):
#     #     with self.session_scope() as session:
#     #         # Start with the base query for ProcessedData
#     #         query = session.query(ProcessedData)
#     #
#     #         # Apply filters dynamically based on the provided arguments
#     #         if user_id is not None:
#     #             query = query.filter(ProcessedData.user_id == user_id)
#     #         if document_id is not None:
#     #             query = query.filter(ProcessedData.document_id == document_id)
#     #         if start_date is not None:
#     #             query = query.filter(ProcessedData.record_date >= start_date)
#     #         if end_date is not None:
#     #             query = query.filter(ProcessedData.record_date <= end_date)
#     #         if associated_with is not None:
#     #             query = query.filter(ProcessedData.associated_with == associated_with)
#     #
#     #         # Apply limit and offset for pagination
#     #         query = query.limit(limit).offset(offset)
#     #
#     #         # self.logger.error(f"File with id  not found")
#     #         # self.logger.debug(f"Executing query: {str(query.statement.compile(compile_kwargs={'literal_binds': True}))}")
#     #
#     #         # Execute the query and fetch the records
#     #         records = query.all()
#     #
#     #         # Extract column names from the ProcessedData model
#     #         column_names = ProcessedData.__table__.columns.keys()
#     #
#     #         # Create the data dictionary
#     #         data = [
#     #             {column: getattr(record, column) for column in column_names}
#     #             for record in records
#     #         ]
#     #
#     #         # Create the DataFrame
#     #         df = pd.DataFrame(data, columns=column_names)
#     #
#     #         return df
#
#     def get_records_by_user_and_document(self, user_id, document_id):
#         with self.session_scope() as session:
#             # Query all columns for the specified user_id and document_id
#             records = session.query(ProcessedData).filter_by(user_id=user_id, document_id=document_id).all()
#
#             # Extract column names from the ProcessedData model
#             column_names = ProcessedData.__table__.columns.keys()
#
#             # Create the data dictionary
#             data = [
#                 {column: getattr(record, column) for column in column_names}
#                 for record in records
#             ]
#
#             # Create the DataFrame
#             df = pd.DataFrame(data, columns=column_names)
#
#             return df
#
#     def create_family(self, user_id, family_name):
#         """
#         Creates a new family group and associates it with the given user.
#
#         :param user_id: ID of the user who is creating the family group.
#         :param family_name: Name of the new family group.
#         :return: The opaque identifier (OID) of the created family group.
#         """
#         with self.session_scope() as session:
#             try:
#                 # Verify that the user exists
#                 user = session.query(User).filter_by(user_id=user_id).first()
#                 if not user:
#                     self.logger.error(f"User with id {user_id} not found.")
#                     raise HTTPException(status_code=404, detail="User not found")
#
#                 # Create the family group
#                 family_group = FamilyGroup(
#                     family_name=family_name,
#                     created_by_user_id=user_id
#                 )
#                 session.add(family_group)
#                 session.flush()  # To get family_group.family_group_id
#
#                 # Add the user to the family group
#                 user_family_group = UserFamilyGroup(
#                     user_id=user_id,
#                     family_group_id=family_group.family_group_id
#                 )
#                 session.add(user_family_group)
#
#                 # Commit the transaction
#                 session.commit()
#                 self.logger.info(f"Family group '{family_name}' created by user_id {user_id}.")
#
#                 return family_group.family_group_oid
#
#             except Exception as e:
#                 session.rollback()
#                 self.logger.error(f"Error creating family group: {str(e)}")
#                 raise HTTPException(status_code=500, detail="Error creating family group")
#
#     def get_selected_records_by_user_and_document(self, user_id, document_id, selected_columns=None):
#         with self.session_scope() as session:
#             # Specify the columns you want to include
#             if selected_columns is None:
#                 selected_columns = [
#                     ProcessedData.record_id,
#                     ProcessedData.text,
#                     ProcessedData.keyword,
#                     # ProcessedData.text,
#                     # ProcessedData.amount,
#                     # ProcessedData.currency,
#                     # ProcessedData.category,
#                     # ProcessedData.subcategory,
#                     # ProcessedData.rationale,
#                     # ProcessedData.refiner_output,
#                     # ProcessedData.categorization_result,
#                     # ProcessedData.categorized_by,
#                     # ProcessedData.datetime,
#                     ProcessedData.associated_with,
#                     # ProcessedData.processed_at,
#                     ProcessedData.is_active,
#                     # ProcessedData.backup_category,
#                     # ProcessedData.backup_subcategory
#                 ]
#
#             # Query the selected columns
#             records = session.query(*selected_columns).filter_by(user_id=user_id, document_id=document_id).all()
#
#             # Extract column names from the selected columns
#             column_names = [column.key for column in selected_columns]
#
#             # Create the data dictionary
#             data = [
#                 {column_names[i]: value for i, value in enumerate(record)}
#                 for record in records
#             ]
#
#             # Create the DataFrame
#             df = pd.DataFrame(data, columns=column_names)
#
#             return df
#
#     def add_record(self, record_data):
#         with self.session_scope() as session:
#             try:
#                 # Create a new ProcessedData object by unpacking the record_data attributes
#                 new_record = ProcessedData(
#                     **record_data.dict(exclude_unset=True)
#                 )
#
#                 # Set the processed_at field if it's not provided
#                 if not new_record.processed_at:
#                     new_record.processed_at = get_current_time()
#
#                 # Add the new record to the session
#                 session.add(new_record)
#
#                 # Commit the transaction to save the new record
#                 session.commit()
#
#                 # Return the newly created record ID
#                 return new_record.record_id
#
#             except SQLAlchemyError as e:
#                 session.rollback()
#                 self.logger.error(f"Error adding record: {str(e)}")
#                 raise HTTPException(status_code=500, detail="Error adding record")
#
#     def delete_file(self, user_id: int, file_id: int, delete_records: bool):
#         with self.session_scope() as session:
#             # Find the file by user_id and file_id
#             file_to_delete = session.query(InitialData).filter_by(user_id=user_id, document_id=file_id).first()
#
#             if not file_to_delete:
#                 self.logger.error(f"File with id {file_id} for user {user_id} not found")
#                 raise HTTPException(status_code=404, detail="File not found")
#
#             # Optionally delete associated records
#             if delete_records:
#                 session.query(ProcessedData).filter_by(document_id=file_id).delete()
#
#             # Delete the file record itself
#             session.delete(file_to_delete)
#
#             # Commit the changes to the database
#             session.commit()
#
#             self.logger.info(
#                 f"File with id {file_id} for user {user_id} deleted successfully along with associated records: {delete_records}")
#
#     def get_categorization_status(self, user_id: int, file_id: int) -> GetCategorizationStatus200Response:
#         with self.session_scope() as session:
#             # Query the InitialData table for the specific user_id and file_id
#             initial_data = session.query(InitialData).filter_by(user_id=user_id, document_id=file_id).first()
#
#             if initial_data:
#                 # Get the number of processed records
#                 # num_processed_records = session.query(ProcessedData).filter_by(document_id=file_id).count()
#
#                 number_of_processed = initial_data.number_of_processed
#
#                 remaining_time_estimation = initial_data.remaining_time_estimation
#                 #  print("------------------type remaining_time_estimation", remaining_time_estimation)
#                 remaining_time_estimation_str = initial_data.remaining_time_estimation_str
#
#                 if not remaining_time_estimation:
#                     remaining_time_estimation = 0
#
#                 # self.logger.debug(f"---------------------------  remaining_time_estimation: {remaining_time_estimation}")
#                 # else:
#
#                 # Prepare the response object
#                 response = GetCategorizationStatus200Response(
#                     remaining_time_estimation=int(remaining_time_estimation),
#                     remaining_time_estimation_str=remaining_time_estimation_str,
#                     status_in_percentage=initial_data.process_status_in_percentage,
#                     status=initial_data.process_status,
#                     num_records=initial_data.number_of_records,
#                     number_of_processed_records=number_of_processed,
#
#                     upload_timestamp=initial_data.upload_timestamp.isoformat() if initial_data.upload_timestamp else None
#                 )
#
#                 return response
#             else:
#                 raise HTTPException(status_code=404, detail="File not found")
#
#     def update_ProcessedData_record(self, record_id, updates):
#         with self.session_scope() as session:
#             record_to_update = session.query(ProcessedData).filter_by(record_id=record_id).first()
#
#             if record_to_update:
#                 for column, value in updates.items():
#                     setattr(record_to_update, column, value)
#
#                 record_to_update.processed_at = datetime.utcnow()
#
#     def get_or_update_exchange_rate(self, date: str, currency: str) -> dict:
#         if not self.secondary_engine:
#             raise RuntimeError("Secondary database is not configured for exchange rates.")
#
#         with self.secondary_session_scope() as session:
#             # Check if exchange rates exist in the secondary database for the given date and currency
#             exchange_rate_record = session.query(HistoricalCurrencyRates).filter_by(date=date,
#                                                                                     currency=currency).first()
#             date_obj = datetime.strptime(date, "%Y-%m-%d").date()
#
#             if exchange_rate_record:
#                 # If exists, return the rates from the secondary database
#                 return {
#                     'rate_to_usd': exchange_rate_record.rate_to_usd,
#                     'usd_to_gold_rate': exchange_rate_record.usd_to_gold_rate,
#                     'usd_to_chf_rate': exchange_rate_record.usd_to_chf_rate
#                 }
#             else:
#                 # If not, fetch from the API (you can handle the logic here to add to secondary database)
#                 # For example, you could call an external API, process the data, and then insert into secondary DB
#                 fetched_rates = self.fetch_exchange_rates_from_api(date, currency)
#                 new_exchange_rate = HistoricalCurrencyRates(
#                     date=date_obj,
#                     currency=currency,
#                     rate_to_usd=fetched_rates['rate_to_usd'],
#                     usd_to_gold_rate=fetched_rates['usd_to_gold_rate'],
#                     usd_to_chf_rate=fetched_rates['usd_to_chf_rate']
#                 )
#                 session.add(new_exchange_rate)
#                 session.commit()
#
#                 return fetched_rates
#
#     def fetch_exchange_rates_from_api(self, date: str, currency: str) -> dict:
#         api_key = "f76057debb5215fbad5bc6b3e72ea349"
#         url = "http://apilayer.net/api/historical"
#         params = {
#             "access_key": api_key,
#             "date": date,
#             "format": 2
#         }
#
#         response = requests.get(url, params=params)
#         if response.status_code == 200:
#             data = response.json()
#             # self.logger.debug(f"API response data: {data}")  # Log the full response for debugging
#             # self.logger.debug(f"Keys in API response data: {list(data.keys())}")
#             if 'quotes' not in data:
#                 self.logger.error("quotes not found")
#                 self.logger.error(f"Missing 'quotes' in the API response for date: {date} and currency: {currency}")
#                 return {
#                     'rate_to_usd': None,
#                     'usd_to_gold_rate': None,
#                     'usd_to_chf_rate': None
#                 }
#
#             else:
#
#                 rate_to_usd = data['quotes'].get(f'USD{currency}')
#                 usd_to_chf_rate = data['quotes'].get('USDCHF')
#                 usd_to_gold_rate = data['quotes'].get('USDXAU')
#
#                 return {
#                     'rate_to_usd': rate_to_usd,
#                     'usd_to_gold_rate': usd_to_gold_rate,
#                     'usd_to_chf_rate': usd_to_chf_rate
#                 }
#
#                 # Insert the new rates into the database
#
#         else:
#             self.logger.error(f"Failed to fetch exchange rates for {date}.")
#             raise HTTPException(status_code=500, detail="Failed to fetch exchange rates")
#
#
#
#     def save_binary_file_to_db(self, path, bank_name, user_id):
#         with self.session_scope() as session:
#             with open(path, 'rb') as file:
#                 file_data = file.read()
#
#             # Determine the file extension
#             file_extension = path.split(".")[-1].lower()
#
#             if file_extension not in ['xlsx', 'xls', 'csv']:
#                 raise ValueError(f"Unsupported file format: {file_extension}")
#
#             # Create the InitialData entry for binary files
#             initial_data_entry = InitialData(
#                 user_id=user_id,
#                 raw_data_format=file_extension,
#                 binary_data=file_data,  # Store the binary data in the BLOB field
#                 associated_with=bank_name,
#                 upload_timestamp=get_current_time(),
#             )
#
#             session.add(initial_data_entry)
#             session.commit()
#             self.document_id = initial_data_entry.document_id
#
#     def save_pdf_to_db(self, path, bank_name, user_id):
#         with self.session_scope() as session:
#             with open(path, 'rb') as file:
#                 file_data = file.read()
#
#             # Encode the PDF data using 'latin-1'
#             encoded_raw_data = file_data.decode('latin-1')
#
#             # Create the InitialData entry for PDF
#             initial_data_entry = InitialData(
#                 user_id=user_id,
#                 raw_data_format='pdf',
#                 encoded_raw_data=encoded_raw_data,
#                 associated_with=bank_name,
#                 upload_timestamp=get_current_time(),
#             )
#
#             session.add(initial_data_entry)
#             session.commit()
#             self.document_id = initial_data_entry.document_id
#
#     def save_raw_file_to_db(self, path, bank_name, user_id):
#         file_extension = path.split(".")[-1].lower()
#
#         if file_extension == 'pdf':
#             self.save_pdf_to_db(path, bank_name, user_id)
#         elif file_extension in ['xlsx', 'xls', 'csv']:
#             self.save_binary_file_to_db(path, bank_name, user_id)
#         else:
#             raise ValueError(f"Unsupported file format: {file_extension}")
#
#     def save_statements_df_to_db(self, user_id, start_date_str, end_date_str, num_records, records_df_serialized):
#         with self.session_scope() as session:
#             last_entry = session.query(InitialData).filter_by(user_id=user_id).order_by(
#                 InitialData.document_id.desc()).first()
#
#             if last_entry:
#                 last_entry.end_date = end_date_str
#                 last_entry.start_date = start_date_str
#                 last_entry.number_of_records = num_records
#                 last_entry.records_df = records_df_serialized
#
#                 session.commit()
#                 self.transfer_df_to_processed_table(session, last_entry.document_id)
#
#
#     def transfer_df_to_processed_table(self, session, document_id: int):
#         initial_data_record = session.query(InitialData).filter(InitialData.document_id == document_id).first()
#         if not initial_data_record:
#             raise ValueError(f"No InitialData record found for document_id {document_id}")
#
#         records_df = pd.read_json(StringIO(initial_data_record.records_df))
#
#         for _, row in records_df.iterrows():
#             raw_row_values = row.to_dict()
#
#             # Get the exchange rate for the record date and currency
#             record_date = raw_row_values['date']
#             currency = raw_row_values.get('currency', '')
#
#             record_date_str = record_date.strftime("%Y-%m-%d")
#
#             # Validate the date format to ensure it's in YYYY-MM-DD
#             try:
#                 datetime.strptime(record_date_str, "%Y-%m-%d")
#             except ValueError:
#                 self.logger.error(f"Invalid date format for record: {record_date_str}. Expected format: YYYY-MM-DD")
#                 raise HTTPException(status_code=400,
#                                     detail=f"Invalid date format: {record_date_str}. Expected format: YYYY-MM-DD")
#
#             exchange_rates = self.get_or_update_exchange_rate(record_date_str, currency)
#
#             rate_to_usd = exchange_rates['rate_to_usd']
#             usd_to_gold_rate = exchange_rates['usd_to_gold_rate']
#             usd_to_chf_rate = exchange_rates['usd_to_chf_rate']
#
#             # Calculate the amount in different currencies
#             amount = raw_row_values.get('amount', 0)
#
#             amount_in_dollar = amount / rate_to_usd  # Converting to USD
#             amount_in_gold = amount / (rate_to_usd * (1 / usd_to_gold_rate))  # Converting to Gold
#             # amount_in_chf = amount / rate_to_chf  # Converting to CHF
#             amount_in_chf = (amount / rate_to_usd) / usd_to_chf_rate
#
#             processed_data_record = ProcessedData(
#                 user_id=initial_data_record.user_id,
#                 document_id=initial_data_record.document_id,
#                 text=raw_row_values.get('text', ''),
#                 cleaned_text=raw_row_values.get('cleaned_text', ''),
#                 keyword=raw_row_values.get('keyword', ''),
#                 amount=amount,
#                 amount_in_dollar=amount_in_dollar,
#                 amount_in_gold=amount_in_gold,
#                 amount_in_chf=amount_in_chf,
#                 currency=currency,
#                 record_date=record_date,
#                 associated_with=initial_data_record.associated_with,
#                 # exchange_rate=rate_to_dollar  # Storing the exchange rate for reference
#             )
#             session.add(processed_data_record)
