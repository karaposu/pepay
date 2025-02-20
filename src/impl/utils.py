
import logging
import yaml
import re
logger = logging.getLogger(__name__)

def create_pepay_db_session(dependencies):

    # pepay_db_session_factory = dependencies.pepay_db_session_factory
    pepay_db_session_factory = dependencies.session_factory


    pepay_db_session_maker = pepay_db_session_factory()
    pepay_db_session = pepay_db_session_maker()
    return pepay_db_session





