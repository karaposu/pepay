
import logging
import yaml
import re
logger = logging.getLogger(__name__)

def create_banks_data_db_session(dependencies):

    banks_db_session_factory = dependencies.bank_info_session_factory
    banks_db_session_maker = banks_db_session_factory()
    banks_db_session = banks_db_session_maker()
    return banks_db_session

def create_budget_db_session(dependencies):

    budget_tracker_session_factory = dependencies.session_factory
    budget_tracker_session_maker = budget_tracker_session_factory()
    budget_tracker_session = budget_tracker_session_maker()
    return budget_tracker_session


def create_exchange_rate_db_session(dependencies):

    exchange_rate_session_factory = dependencies.exchange_rate_session_factory
    exchange_rate_session_maker = exchange_rate_session_factory()
    exchange_rate_session = exchange_rate_session_maker()
    return exchange_rate_session


def get_currencies_by_country(yaml_file_path: str, country_code: str) -> str:
    try:
        with open(yaml_file_path, 'r', encoding='utf-8') as file:
            country_currency_data = yaml.safe_load(file)

        country_code = country_code.upper()

        if country_code in country_currency_data:
            currencies = country_currency_data[country_code].get('currencies')
            if not currencies:
                # logger.error(f"The country code '{country_code}' has no associated currencies.")
                return None
            elif isinstance(currencies, list):
                return currencies[0]
            else:
                return currencies
        else:
            logger.error(f"Country code '{country_code}' not found in the YAML file.")
            return None

    except FileNotFoundError:
        logger.error(f"Error: The file '{yaml_file_path}' was not found.")
        return None
    except yaml.YAMLError as exc:
        logger.error(f"Error parsing YAML file: {exc}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return None


def sanitize_bank_name(bank_name):
    """
    Sanitizes the bank_name to create a temporary string_bank_id.
    """
    # Remove leading/trailing whitespace
    bank_name = bank_name.strip()
    # Convert to lowercase
    bank_name = bank_name.lower()
    # Replace non-alphanumeric characters with underscores
    bank_name = re.sub(r'\W+', '_', bank_name)
    # Remove multiple underscores
    bank_name = re.sub(r'_+', '_', bank_name)
    # Remove leading/trailing underscores
    bank_name = bank_name.strip('_')
    return bank_name



