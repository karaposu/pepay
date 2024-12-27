# db/models/bank_db_models.py

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from datetime import datetime
import json
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Bank(Base):
    __tablename__ = 'banks'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    string_id = Column(String, nullable=True)
    support_note = Column(String, nullable=True)
    base_country = Column(String(255), nullable=False)
    available_currencies = Column(Text)  # JSON serialized list
    supported = Column(Boolean, default=False)
    soon_supported = Column(Boolean, default=False)
    popularity = Column(Integer, default=5)  # Should be between 1 and 10
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    logo = Column(String(255))
    illustration = Column(String(255))
    aliases = Column(Text)  # JSON serialized list
    is_international = Column(Boolean, default=False)

    supported_file_formats = Column(Text, nullable=True)  # Store supported formats as JSON

    def set_aliases(self, alias_list):
        self.aliases = json.dumps(alias_list)

    def get_aliases(self):
        return json.loads(self.aliases) if self.aliases else []

    def set_supported_file_formats(self, formats_list):
        self.supported_file_formats = json.dumps(formats_list)

    def get_supported_file_formats(self):
        return json.loads(self.supported_file_formats) if self.supported_file_formats else []

    def set_available_currencies(self, currencies_list):
        self.available_currencies = json.dumps(currencies_list)

    def get_available_currencies(self):
        return json.loads(self.available_currencies) if self.available_currencies else []




