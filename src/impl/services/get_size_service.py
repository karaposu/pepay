

import logging
from fastapi import HTTPException
from datetime import datetime
from traceback import format_exc

from models.community_graph_get200_response_inner import CommunityGraphGet200ResponseInner
from db.models.community_size  import CommunitySize

logger = logging.getLogger(__name__)

class GetCommunitySize:
    def __init__(self, dependencies):
        self.dependencies = dependencies
        self.response = None

        logger.debug("Inside GetCommunitySize service")

        try:
            self.preprocess_request_data()
            self.process_request()
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}\n{format_exc()}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def preprocess_request_data(self):
        # No specific request data to parse for this service
        pass

    def process_request(self):
        # Access session factory from dependencies
        # session_factory = self.dependencies.session_factory()
        community_session_factory = self.dependencies.community_db_session_factory()
        session = community_session_factory()
        
        try:
            logger.debug("Querying community_size table...")

            # Retrieve all records ordered by value_date
            records = (session.query(CommunitySize)
                               .order_by(CommunitySize.value_date.asc())
                               .all())
            logger.debug(f"Number of community size records found: {len(records)}")

            # Construct the response list
            response_list = []
            for record in records:
                # Map to the schema for CommunityGraphGet200ResponseInner
                entry = CommunityGraphGet200ResponseInner(
                    date=record.value_date.strftime("%Y-%m-%d"),
                    telegram_size=record.telegram or 0,
                    discord_size=record.discord or 0,
                    reddit_size=record.reddit or 0
                )
                response_list.append(entry)

            self.response = response_list

        except HTTPException as http_exc:
            session.rollback()
            logger.error(f"HTTPException during community size retrieval: {http_exc.detail}")
            raise http_exc
        except Exception as e:
            session.rollback()
            logger.error(f"An error occurred during community size retrieval: {e}\n{format_exc()}")
            raise HTTPException(status_code=500, detail="Internal server error")
        finally:
            session.close()
