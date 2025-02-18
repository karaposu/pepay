# db/repositories/bank_information_repository.py

from sqlalchemy.orm import Session
import logging
import json


from db.models.transfer_builder import TransferBuilder

logger = logging.getLogger(__name__)

class BuypepecoinEepository:
    def __init__(self, session: Session):
        self.session = session

    def save_initial_request_to_transfer_builder(self, request):
       # query = self.session.

   