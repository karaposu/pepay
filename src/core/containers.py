# here is core/containers.py
from dependency_injector import containers, providers

import logging
logger = logging.getLogger(__name__)
import os


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from db.repositories.user_repository import UserRepository
# from db.repositories.file_repository import FileRepository
from db.session import get_engine
import yaml

from db.repositories.buypepecoin_repository import BuypepecoinRepository
# from db.repositories.report_repository import ReportRepository

# from utils.currency_utils import load_currency_configs

class Services(containers.DeclarativeContainer):
    config = providers.Configuration()

    # Engine provider
    engine = providers.Singleton(
        create_engine,
        config.db_url,
        echo=False
    )

    # # Session factory provider
    session_factory = providers.Singleton(
        sessionmaker,
        bind=engine
    )


    # community_db Engine provider
    community_db_engine = providers.Singleton(
        create_engine,
        config.community_db_url,
        echo=False
    )

    # community db Session factory provider
    community_db_session_factory = providers.Singleton(
        sessionmaker,
        bind=community_db_engine
    )


    buypepecoin_repository_provider = providers.Factory(
        BuypepecoinRepository,
        session=providers.Dependency()
    )



    



