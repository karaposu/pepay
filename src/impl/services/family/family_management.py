from impl.services.base_service import BaseService
from datetime import datetime

from db.db_manager import DBManager

import logging
logger = logging.getLogger(__name__)


import tempfile
import os

def get_current_time():
    return datetime.utcnow()



class FamilyCreator(BaseService):
    def check_compatibility(self, img=None, text=None):
        return True, ""

    def initialize_db_manager(self):
        # db_path = os.path.join(os.path.dirname(__file__), "..", "..", "budget_tracker.db")
        db_path = os.path.join(os.path.dirname(__file__), "..", "..", "db/budget_tracker.db")
        db_path = os.path.abspath(db_path)
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database file not found at: {db_path}")
        if not os.access(db_path, os.W_OK):
            raise PermissionError(f"Database file is not writable: {db_path}")

        try:
            return DBManager(db_path)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize DBManager: {e}")


    def preprocess_request_data(self):
        db_manager = self.initialize_db_manager()


        user_id = self.request.user_id
        family_name = self.request.family_name

        family_group_oid=db_manager.create_family(user_id, family_name)

        response= {

            "family_group_oid":family_group_oid,
            "family_name":family_name ,

        }


        self.preprocessed_data=response

    def process_request(self):
        self.response=self.preprocessed_data


