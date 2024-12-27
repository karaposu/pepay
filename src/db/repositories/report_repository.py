# db/repositories/report_repository.py

from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from datetime import datetime
import calendar
from typing import Dict, List, Any
import logging

from db.models import ProcessedData
from models.selected_period_aggregation import SelectedPeriodAggregation
from models.totals import Totals

from db.repositories.user_repository import UserRepository  # Import UserRepository
from models.currency_config import CurrencyConfig
from models.scatter_report import ScatterReport

from models.monthly_frequency import MonthlyFrequency


logger = logging.getLogger(__name__)

class IncomeAndSpending:
    def __init__(
        self,
        no_data_flag: bool,
        total_income: float,
        total_spending: float
    ):
        self.no_data_flag = no_data_flag
        self.total_income = total_income
        self.total_spending = total_spending

class ReportRepository:
    def __init__(self, session: Session, currency_configs: Dict[str, Dict], user_repository: UserRepository):
        self.session = session
        self.currency_configs = currency_configs  # Add this line
        self.user_repository = user_repository  # Add this line


    def create_a_scatter_report(
        self,
        user_id: int,
        bank_account_id: int,
        start_date: str,
        end_date: str,
        master_category_list: Dict[str, List[str]],
        currency: str,
        category: str = None,
        subcategory: str = None
    ) -> List[ScatterReport]:
        logger.debug("Creating scatter report")

        # Convert start_date and end_date if provided, otherwise set defaults
        if start_date is None:
            start_date = datetime(2000, 1, 1)
        else:
            start_date = datetime.fromisoformat(start_date)
        if end_date is None:
            end_date = datetime(2040, 1, 1)
        else:
            end_date = datetime.fromisoformat(end_date)

        # Handle currency
        if currency:
            currency_code = currency.upper()
        else:
            # If currency not provided, try user default
            user_settings = self.user_repository.get_user_settings(user_id)
            if user_settings and user_settings.default_currency:
                currency_code = user_settings.default_currency.upper()
            else:
                currency_code = "USD"

        currency_config = self.get_currency_config(currency_code)
        if not currency_config:
            logger.error(f" (report_repository.py ) Currency config not found for {currency_code}")
            raise HTTPException(status_code=400, detail=f"Unsupported currency code: {currency_code}")

        # Map currency_code to the corresponding column in ProcessedData
        currency_column_map = {
            'USD': ProcessedData.amount_in_dollar,
            'XAU': ProcessedData.amount_in_gold,
            'CHF': ProcessedData.amount_in_chf,
            'TRY': ProcessedData.amount,  # Original currency
            # Add other currencies if supported
        }

        # If currency code is not found, default to a known column or raise error
        amount_column = currency_column_map.get(currency_code, ProcessedData.amount_in_dollar)

        # Build the base query
        query = self.session.query(
            func.date(ProcessedData.record_date).label('day'),
            ProcessedData.category,
            ProcessedData.subcategory,
            func.count(ProcessedData.record_id).label('frequency'),
            func.sum(amount_column).label('total_amount')
        ).filter(
            ProcessedData.user_id == user_id,
            ProcessedData.record_date >= start_date,
            ProcessedData.record_date <= end_date
        )

        # Filter by bank_account_id if provided
        if bank_account_id is not None:
            # Assuming bank_account_id corresponds to ProcessedData.document_id or related field
            # Adjust this filter if your schema is different
            query = query.filter(ProcessedData.document_id == bank_account_id)

        # Filter by category if provided
        if category:
            query = query.filter(ProcessedData.category == category)

        # Filter by subcategory if provided
        if subcategory:
            query = query.filter(ProcessedData.subcategory == subcategory)

        query = query.group_by(
            func.date(ProcessedData.record_date),
            ProcessedData.category,
            ProcessedData.subcategory
        )

        results = query.all()

        scatter_reports = []
        for day, cat, subcat, freq, total_amt in results:
            # day is a string representing date (due to func.date), convert back if needed
            # If the DB returns datetime objects directly, adjust accordingly.
            if isinstance(day, str):
                day_obj = datetime.strptime(day, "%Y-%m-%d")
            else:
                day_obj = day  # If already a datetime

            day_of_week = day_obj.strftime("%A")  # Monday, Tuesday, etc.

            # Only include category and subcategory that are in the master_category_list if needed
            # If you want to filter out categories not in master list:
            # if cat and cat not in master_category_list:
            #     continue
            # if subcat and cat in master_category_list and subcat not in master_category_list[cat]:
            #     continue

            scatter_report = ScatterReport(
                date=day_obj.strftime("%Y-%m-%d"),
                frequency=freq,
                day_of_week=day_of_week,
                category=cat,
                subcategory=subcat,
                total_amount=total_amt,
                currency=currency_code
            )
            scatter_reports.append(scatter_report)

        return scatter_reports

    def aggregate_income_and_spending(
            self,
            user_id: int,
            bank_account_id: int,
            start_date: str,
            end_date: str,
            currency_code: str  # Added parameter
    ) -> IncomeAndSpending:
        def apply_bank_account_filter(query):
            if bank_account_id is not None:
                return query.filter(ProcessedData.document_id == bank_account_id)
            return query

        logger.debug("inside aggregate_income_and_spending")

        if start_date is None:
            start_date = datetime(2000, 1, 1)
        if end_date is None:
            end_date = datetime(2040, 1, 1)


        data_exists = apply_bank_account_filter(
            self.session.query(ProcessedData.record_id)
            .filter(
                ProcessedData.user_id == user_id,
                ProcessedData.record_date >= start_date,
                ProcessedData.record_date <= end_date,
            )
        ).first() is not None

        logger.debug(f"data_exists {data_exists}")

        if not data_exists:
            return IncomeAndSpending(
                no_data_flag=True,
                total_income=0,
                total_spending=0
            )

        # Map currency_code to the corresponding column in ProcessedData
        currency_column_map = {
            'USD': ProcessedData.amount_in_dollar,
            'XAU': ProcessedData.amount_in_gold,
            'CHF': ProcessedData.amount_in_chf,
            'TRY': ProcessedData.amount,  # Original currency
            # Add other currencies if you have them in your database
        }

        # if currency_code not in currency_column_map:
        #     logger.error(f"Unsupported currency code: {currency_code}")
        #     raise HTTPException(status_code=400, detail=f"Unsupported currency code: {currency_code}")

        amount_column = currency_column_map[currency_code]

        # Calculate total income
        total_income = apply_bank_account_filter(
            self.session.query(func.sum(amount_column))
            .filter(
                ProcessedData.user_id == user_id,
                ProcessedData.record_date >= start_date,
                ProcessedData.record_date <= end_date,
                ProcessedData.amount > 0  # Positive amounts as income
            )
        ).scalar() or 0

        logger.debug("Calculated total_income")

        # Calculate total spending
        total_spending = apply_bank_account_filter(
            self.session.query(func.sum(amount_column))
            .filter(
                ProcessedData.user_id == user_id,
                ProcessedData.record_date >= start_date,
                ProcessedData.record_date <= end_date,
                ProcessedData.amount < 0  # Negative amounts as spending
            )
        ).scalar() or 0

        logger.debug("Calculated total_spending")

        return IncomeAndSpending(
            no_data_flag=False,
            total_income=total_income,
            total_spending=total_spending
        )

    def query_category_totals(
            self,
            user_id: int,
            bank_account_id: int,
            start_date: str,
            end_date: str,
            currency_code: str  # Added parameter
    ):   
        logger.debug(
            f"Querying category totals for user_id: {user_id}, bank_account_id: {bank_account_id}, start_date: {start_date}, end_date: {end_date}"
        )
        
        if start_date is None:
            start_date = datetime(2000, 1, 1)
        if end_date is None:
            end_date = datetime(2040, 1, 1)

        # Map currency_code to the corresponding column in ProcessedData
        currency_column_map = {
            'USD': ProcessedData.amount_in_dollar,
            'XAU': ProcessedData.amount_in_gold,
            'CHF': ProcessedData.amount_in_chf,
            'TRY': ProcessedData.amount,  # Original currency
            # Add other currencies if applicable
        }

        if currency_code not in currency_column_map:
            logger.error(f"Unsupported currency code: {currency_code}")
            raise HTTPException(status_code=400, detail=f"Unsupported currency code: {currency_code}")

        amount_column = currency_column_map[currency_code]

        query = self.session.query(
            ProcessedData.category,
            ProcessedData.subcategory,
            func.sum(amount_column).label('total_amount')
        ).filter(
            ProcessedData.user_id == user_id,
            ProcessedData.record_date >= start_date,
            ProcessedData.record_date <= end_date
        )

        if bank_account_id is not None:
            query = query.filter(ProcessedData.document_id == bank_account_id)

        results = query.group_by(
            ProcessedData.category,
            ProcessedData.subcategory
        ).all()

        return results

    def aggregate_and_format_categories(
            self,
            queried_data,
            master_category_list: Dict[str, List[str]],
            currency_code: str  # Added parameter
    ):
        logger.debug(f"Aggregating and formatting categories from queried data.")

        currency_config = self.get_currency_config(currency_code)
        if not currency_config:
            raise HTTPException(status_code=400, detail=f"Unsupported currency code: {currency_code}")

        category_dict = {
            category: {
                "total": 0,
                "subcategories": []
            } for category in master_category_list
        }

        for category, subcategory, total_amount in queried_data:
            logger.debug(f"Processing category: {category}, subcategory: {subcategory}, total: {total_amount}")
            if category in category_dict:
                if subcategory in master_category_list[category]:
                    category_dict[category]["total"] += total_amount
                    category_dict[category]["subcategories"].append({
                        "name": subcategory,
                        "total_amount": total_amount,
                        "currency": currency_code,
                        "currency_config": currency_config
                    })

        logger.debug(f"Category dictionary before formatting: {category_dict}")

        category_aggregations = []
        for category_name, data in category_dict.items():
            if data["total"] != 0:
                category_aggregations.append({
                    "category_name": category_name,
                    "total": data["total"],
                    "currency": currency_code,
                    "currency_config": currency_config,
                    "subcategories": data["subcategories"]
                })

        logger.debug(f"Final category aggregations: {category_aggregations}")
        return category_aggregations

    def aggregate_categories_and_subcategories(
            self,
            user_id: int,
            bank_account_id: int,
            start_date: str,
            end_date: str,
            master_category_list: Dict[str, List[str]],
            currency_code: str  # Added parameter
    ):
        queried_data = self.query_category_totals(
            user_id, bank_account_id, start_date, end_date, currency_code
        )
        category_aggregations = self.aggregate_and_format_categories(
            queried_data, master_category_list, currency_code
        )
        return category_aggregations

    def get_currency_config(self, currency_code: str) -> CurrencyConfig:
        currency_data = self.currency_configs.get(currency_code.upper())

        if currency_data:
            return CurrencyConfig(
                symbol=currency_data.get('symbol'),
                name=currency_data.get('name'),
                symbol_native=currency_data.get('symbol_native'),
                fractional_digits=currency_data.get('decimal_digits'),
                rounding=currency_data.get('rounding'),
                name_plural=currency_data.get('name_plural'),
                symbol_placement=currency_data.get('symbol_placement', 'front')  # Default to 'front' if not specified
            )
        else:
            logger.warning(f"Currency config not found for {currency_code}")
            return None  # Or raise an exception if preferred
    
    def create_a_report(
            self,
            user_id: int,
            bank_account_id: int,
            start_date: str,
            end_date: str,
            master_category_list: Dict[str, List[str]],
            currency: str
    ) -> SelectedPeriodAggregation:
        logger.debug("inside create_a_report ")

        if start_date is None:
            start_date = datetime(2000, 1, 1)
        if end_date is None:
            end_date = datetime(2040, 1, 1)

        # Use the provided currency parameter
        if currency:
            currency_code = currency.upper()
        else:
            # If currency is not provided, fall back to user's default currency
            user_settings = self.user_repository.get_user_settings(user_id)
            if user_settings and user_settings.default_currency:
                currency_code = user_settings.default_currency
            else:
                currency_code = "USD(d)"  # Default currency
        
        # Get the CurrencyConfig for the specified currency
        currency_config = self.get_currency_config(currency_code)
        if not currency_config:
            logger.error(f"Currency config not found for {currency_code}")
            raise HTTPException(status_code=400, detail=f"Unsupported currency code: {currency_code}")

        # Aggregate income and spending
        income_and_spending = self.aggregate_income_and_spending(
            user_id, bank_account_id, start_date, end_date, currency_code
        )
        logger.debug("income_and_spending calculated ")

        if income_and_spending.no_data_flag:
            report = SelectedPeriodAggregation(
                category_aggregations=[],
                total_income=0,
                total_spending=0,
                currency=currency_code,
                currency_config=currency_config
            )
            return report

        # Aggregate categories and subcategories
        category_aggregations = self.aggregate_categories_and_subcategories(
            user_id, bank_account_id, start_date, end_date, master_category_list, currency_code
        )

        report = SelectedPeriodAggregation(
            category_aggregations=category_aggregations,
            total_income=income_and_spending.total_income,
            total_spending=income_and_spending.total_spending,
            currency=currency_code,
            currency_config=currency_config
        )
        return report
   
    def create_historical_report(
        self,
        user_id: int,
        bank_account_id: int,
        start_date_filter: str = None,
        end_date_filter: str = None,
        master_category_list: Dict[str, List[str]] = None,
        currency: str = None
    ) -> List[Dict[str, Any]]:
        logger.debug(
            f"Creating historical report for user_id: {user_id}, bank_account_id: {bank_account_id}, "
            f"start_date_filter: {start_date_filter}, end_date_filter: {end_date_filter}, currency: {currency}"
        )

        # Determine currency code
        if currency:
            currency_code = currency.upper()
        else:
            # If currency is not provided, fall back to user's default currency
            user_settings = self.user_repository.get_user_settings(user_id)
            if user_settings and user_settings.default_currency:
                currency_code = user_settings.default_currency.upper()
            else:
                currency_code = "USD"

        # Get the currency config
        currency_config = self.get_currency_config(currency_code)
        if not currency_config:
            logger.error(f"(create_historical_report) Currency config not found for {currency_code}")
            raise HTTPException(status_code=400, detail=f"Unsupported currency code: {currency_code}")

        # Convert start_date_filter and end_date_filter to datetimes or defaults
        if start_date_filter:
            start_date_obj = datetime.fromisoformat(start_date_filter)
        else:
            start_date_obj = datetime(2000, 1, 1)

        if end_date_filter:
            end_date_obj = datetime.fromisoformat(end_date_filter)
        else:
            end_date_obj = datetime(2030, 1, 1)

        # Query months within the given period
        query = self.session.query(
            func.strftime('%Y-%m', ProcessedData.record_date).label('month')
        ).filter(
            ProcessedData.user_id == user_id,
            ProcessedData.record_date >= start_date_obj,
            ProcessedData.record_date <= end_date_obj
        )

        if bank_account_id is not None:
            query = query.filter(ProcessedData.document_id == bank_account_id)

        months = query.group_by(
            func.strftime('%Y-%m', ProcessedData.record_date)
        ).all()

        logger.debug(f"Found months: {months}")

        historical_aggregations = []

        for month_tuple in months:
            month = month_tuple[0]
            logger.debug(f"Processing month: {month}")

            # Compute the start and end date for the given month
            month_start_date = f"{month}-01"
            month_end_date = f"{month}-{self.get_last_day_of_month(month)}"
            logger.debug(f"Month start_date: {month_start_date}, end_date: {month_end_date}")

            # Aggregate income and spending for the month
            income_and_spending = self.aggregate_income_and_spending(
                user_id, bank_account_id, month_start_date, month_end_date, currency_code
            )
            logger.debug(
                f"For {month}: Total income = {income_and_spending.total_income}, "
                f"Total spending = {income_and_spending.total_spending}"
            )

            # Aggregate categories for the month
            category_aggregations = self.aggregate_categories_and_subcategories(
                user_id, bank_account_id, month_start_date, month_end_date, master_category_list, currency_code
            )
            logger.debug(f"Category aggregations for {month}: {category_aggregations}")

            # Append the month's data
            historical_aggregations.append({
                "month": month,
                "category_aggregations": category_aggregations,
                "total_income": income_and_spending.total_income,
                "total_spending": income_and_spending.total_spending,
                "currency": currency_code,
                "currency_config": currency_config.model_dump()
            })

        logger.debug(f"Final historical aggregations: {historical_aggregations}")
        return historical_aggregations


    # def create_historical_report(
    #         self,
    #         user_id: int,
    #         bank_account_id: int,
    #         start_date_filter,
    #         end_date_filter,
    #         master_category_list: Dict[str, List[str]],
    #         currency: str = None
    # ) -> List[Dict[str, Any]]:
    #     logger.debug(f"Creating historical report for user_id: {user_id}, bank_account_id: {bank_account_id}, currency: {currency}")

    #     # Determine currency code
    #     if currency:
    #         currency_code = currency.upper()
    #     else:
    #         # If currency is not provided, fall back to user's default currency
    #         user_settings = self.user_repository.get_user_settings(user_id)
    #         if user_settings and user_settings.default_currency:
    #             currency_code = user_settings.default_currency.upper()
    #         else:
    #             currency_code = "USD"

    #     # Get the currency config
    #     currency_config = self.get_currency_config(currency_code)
    #     if not currency_config:
    #         logger.error(f"(create_historical_report) Currency config not found for {currency_code}")
    #         raise HTTPException(status_code=400, detail=f"Unsupported currency code: {currency_code}")

    #     # Query months
    #     query = self.session.query(
    #         func.strftime('%Y-%m', ProcessedData.record_date).label('month')
    #     ).filter(
    #         ProcessedData.user_id == user_id
    #     )

    #     if bank_account_id is not None:
    #         query = query.filter(ProcessedData.document_id == bank_account_id)

    #     months = query.group_by(
    #         func.strftime('%Y-%m', ProcessedData.record_date)
    #     ).all()

    #     logger.debug(f"Found months: {months}")

    #     historical_aggregations = []

    #     for month_tuple in months:
    #         month = month_tuple[0]
    #         logger.debug(f"Processing month: {month}")

    #         # Get start_date and end_date for the month
    #         start_date = f"{month}-01"
    #         end_date = f"{month}-{self.get_last_day_of_month(month)}"
    #         logger.debug(f"Start date: {start_date}, End date: {end_date}")

    #         # Aggregate income and spending for the month in chosen currency
    #         income_and_spending = self.aggregate_income_and_spending(
    #             user_id, bank_account_id, start_date, end_date, currency_code
    #         )
    #         logger.debug(
    #             f"Total income: {income_and_spending.total_income}, Total spending: {income_and_spending.total_spending}"
    #         )

    #         # Aggregate categories and subcategories for the month in chosen currency
    #         category_aggregations = self.aggregate_categories_and_subcategories(
    #             user_id, bank_account_id, start_date, end_date, master_category_list, currency_code
    #         )
    #         logger.debug(f"Category aggregations for {month}: {category_aggregations}")

    #         # Add to historical aggregations
    #         historical_aggregations.append({
    #             "month": month,
    #             "category_aggregations": category_aggregations,
    #             "total_income": income_and_spending.total_income,
    #             "total_spending": income_and_spending.total_spending,
    #             "currency": currency_code,
    #             "currency_config": currency_config.model_dump()
    #         })

    #     logger.debug(f"Final historical aggregations: {historical_aggregations}")
    #     return historical_aggregations

    def get_last_day_of_month(self, month: str) -> int:
        # Helper method to get the last day of a month in YYYY-MM format
        year, month_num = map(int, month.split('-'))
        return calendar.monthrange(year, month_num)[1]
    

    def query_category_frequency(self,
        user_id: int,
        bank_account_id: int,
        start_date: str,
        end_date: str
    ):
        logger.debug(
            f"Querying category frequency for user_id: {user_id}, bank_account_id: {bank_account_id}, start_date: {start_date}, end_date: {end_date}"
        )

        # Convert start_date and end_date to datetime if they are strings
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date)

        query = self.session.query(
            ProcessedData.category,
            ProcessedData.subcategory,
            func.count(ProcessedData.record_id).label('frequency')
        ).filter(
            ProcessedData.user_id == user_id,
            ProcessedData.record_date >= start_date,
            ProcessedData.record_date <= end_date
        )

        if bank_account_id is not None:
            query = query.filter(ProcessedData.document_id == bank_account_id)

        results = query.group_by(
            ProcessedData.category,
            ProcessedData.subcategory
        ).all()

        return results
    


    def aggregate_and_format_categories_frequency(self,
                                                  queried_data,
                                                    master_category_list: Dict[str, List[str]]
    ):
        logger.debug("Aggregating and formatting categories by frequency.")

        # Initialize category dict with empty frequency info
        category_dict = {
            category: {
                "frequency": 0,
                "subcategories": []
            } for category in master_category_list
        }

        # Fill category_dict with frequency data
        for category, subcategory, freq in queried_data:
            if category in category_dict:
                # Only consider subcategories in the master list if needed
                if subcategory in master_category_list.get(category, []):
                    category_dict[category]["frequency"] += freq
                    category_dict[category]["subcategories"].append({
                        "name": subcategory,
                        "frequency": freq
                    })

        # Convert to the desired CategoryAggregation-like structure
        category_aggregations = []
        for category_name, data in category_dict.items():
            # Only add category if frequency > 0 or if you want to add empty ones
            if data["frequency"] > 0:
                category_aggregations.append({
                    "category_name": category_name,
                    # total, currency, and currency_config might not be needed if we only do frequency
                    # set them to None or omit as per your schema definition.
                    "total": None,
                    "currency": None,
                    "currency_config": None,
                    "frequency": data["frequency"],
                    "subcategories": [
                        {
                            "name": s["name"],
                            "frequency": s["frequency"],
                            # no amount or currency for frequency-only endpoint, set them None or omit
                            "total_amount": None
                        } for s in data["subcategories"]
                    ]
                })

        return category_aggregations
    



    def create_historical_freq_report(self,user_id: int,
                                      bank_account_id: int,
                                      master_category_list: Dict[str, List[str]],
                                      start_date: str = None,
                                      end_date: str = None
                                     ) -> List[Dict[str, Any]]:
        logger.debug(f"Creating historical frequency report for user_id: {user_id}, bank_account_id: {bank_account_id}, start_date: {start_date}, end_date: {end_date}")

        # Convert start_date and end_date to datetime or set defaults
        if start_date is None:
            start_date_obj = datetime(2000, 1, 1)
        else:
            start_date_obj = datetime.fromisoformat(start_date)

        if end_date is None:
            end_date_obj = datetime(2040, 1, 1)
        else:
            end_date_obj = datetime.fromisoformat(end_date)

        # Query months within the given period
        query = self.session.query(
            func.strftime('%Y-%m', ProcessedData.record_date).label('month')
        ).filter(
            ProcessedData.user_id == user_id,
            ProcessedData.record_date >= start_date_obj,
            ProcessedData.record_date <= end_date_obj
        )

        if bank_account_id is not None:
            query = query.filter(ProcessedData.document_id == bank_account_id)

        months = query.group_by(
            func.strftime('%Y-%m', ProcessedData.record_date)
        ).all()

        logger.debug(f"Found months: {months}")

        historical_frequencies = []

        for month_tuple in months:
            month = month_tuple[0]
            logger.debug(f"Processing month: {month}")

            # Calculate the start_date and end_date for this month
            month_start_date = f"{month}-01"
            month_end_date = f"{month}-{self.get_last_day_of_month(month)}"

            # Query category frequency data for this month
            category_freq_data = self.query_category_frequency(
                user_id, bank_account_id, month_start_date, month_end_date
            )

            # Aggregate category frequencies
            category_aggregations = self.aggregate_and_format_categories_frequency(
                category_freq_data, master_category_list
            )

            # Compute total_frequency as sum of all category frequencies
            total_frequency = sum(cat["frequency"] for cat in category_aggregations if cat.get("frequency"))

            # Add to the historical frequencies
            # Note: since we don't need currency or amounts, we omit them.
            historical_frequencies.append({
                "month": month,
                "category_aggregations": category_aggregations,
                "total_frequency": total_frequency
            })

        logger.debug(f"Final historical frequency data: {historical_frequencies}")
        return historical_frequencies






    

    def create_a_total_report(
            self,
            user_id: int,
            bank_account_id: int,
            start_date: str,
            end_date: str,
            currency: str
    ) -> Totals:
        logger.debug("inside create_a_total_method ")

        # Handle date defaults if not provided
        if start_date is None:
            start_date = datetime(2000, 1, 1)
        else:
            # Convert ISO string to datetime
            start_date = datetime.fromisoformat(start_date)

        if end_date is None:
            end_date = datetime(2040, 1, 1)
        else:
            # Convert ISO string to datetime
            end_date = datetime.fromisoformat(end_date)

        # Determine currency code
        if currency:
            currency_code = currency.upper()
        else:
            # If currency is not provided, try user's default
            user_settings = self.user_repository.get_user_settings(user_id)
            if user_settings and user_settings.default_currency:
                currency_code = user_settings.default_currency.upper()
            else:
                currency_code = "USD"

        # Get the CurrencyConfig for the specified currency
        currency_config = self.get_currency_config(currency_code)
        if not currency_config:
            logger.error(f"Currency config not found for {currency_code}")
            raise HTTPException(status_code=400, detail=f"Unsupported currency code: {currency_code}")

        # Aggregate income and spending
        income_and_spending = self.aggregate_income_and_spending(
            user_id=user_id,
            bank_account_id=bank_account_id,
            start_date=start_date,
            end_date=end_date,
            currency_code=currency_code
        )
        logger.debug("income_and_spending calculated ")

        # Create a Totals object
        # If no_data_flag is True, total_income and total_spending will be 0 anyway
        totals = Totals(
            currency=currency_code,
            currency_config=currency_config,
            total_income=income_and_spending.total_income,
            total_spending=income_and_spending.total_spending
        )

        return totals
    
    




