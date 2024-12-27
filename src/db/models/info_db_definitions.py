# # db/models/info_db_definitons.py
#
# from sqlalchemy import create_engine, Column, Integer, String, Boolean, LargeBinary, Text, Date, DateTime
#
# from sqlalchemy.orm import declarative_base
# from sqlalchemy.orm import sessionmaker
# from datetime import datetime
# import json
# import yaml
# import os
# # Base for the fixed data database
# FixedDataBase = declarative_base()
#
# # Create a separate engine and session for the fixed data
# fixed_data_engine = create_engine('sqlite:///fixed_data.db')  # Example for SQLite, change it to your preferred database
# FixedDataSession = sessionmaker(bind=fixed_data_engine)
#
# # Create a context manager to handle sessions
# class FixedDataManager:
#     def __init__(self):
#         self.engine = fixed_data_engine
#         self.session = FixedDataSession()
#
#     def __enter__(self):
#         return self.session
#
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         if exc_type:
#             self.session.rollback()
#         else:
#             self.session.commit()
#         self.session.close()
#
# # def load_file_as_binary(file_path):
# #     """Utility function to load a file as binary data."""
# #     if os.path.exists(file_path):
# #         with open(file_path, 'rb') as f:
# #             return f.read()
# #     return None
#
# def load_file_as_binary(file_path):
#     """Utility function to load a file as binary data."""
#     if file_path and os.path.exists(file_path):  # Check if file_path is not None and exists
#         with open(file_path, 'rb') as f:
#             return f.read()
#     return None
#
#
#   # soon_supported = Column(Boolean, default=False)
#   # updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
#   # popularity
#   # currency_code = Column(String(3), nullable=True)
#
#
# # Define the BankInformation table
# # Define the BankInformation table
# class BankInformation(FixedDataBase):
#     __tablename__ = 'bank_information'
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     name = Column(String, nullable=False)
#     string_id = Column(String, nullable=True)
#     aliases = Column(Text, nullable=True)
#     info = Column(Text, nullable=True)
#     notes = Column(Text, nullable=True)
#     logo = Column(String, nullable=True)  # Logo is optional (nullable=True)
#     supported = Column(Boolean, default=False)
#     soon_supported = Column(Boolean, default=False)
#     illustration = Column(String, nullable=True) # Illustration is optional (nullable=True)
#     country = Column(String, nullable=False)
#     website_url = Column(String, nullable=True)
#     customer_support_number = Column(String, nullable=True)
#     established_date = Column(Date, nullable=True)
#     updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
#     available_services = Column(Text, nullable=True)
#     currency_code = Column(String(3), nullable=True)
#     is_international = Column(Boolean, default=False)
#     tier = Column(Integer, nullable=True)
#
#     supported_file_formats = Column(Text, nullable=True)  # Store supported formats as JSON
#
#     def set_aliases(self, alias_list):
#         self.aliases = json.dumps(alias_list)
#
#     def get_aliases(self):
#         return json.loads(self.aliases) if self.aliases else []
#
#     def set_supported_file_formats(self, formats_list):
#         self.supported_file_formats = json.dumps(formats_list)
#
#     def get_supported_file_formats(self):
#         return json.loads(self.supported_file_formats) if self.supported_file_formats else []
#
# FixedDataBase.metadata.create_all(fixed_data_engine)
#
#
# def load_yaml(file_path):
#     with open(file_path, 'r', encoding='utf-8') as file:
#         return yaml.safe_load(file)
#
#
# def update_banks_from_yaml(file_path):
#     # Load the YAML data
#     banks_data = load_yaml(file_path)
#
#     with FixedDataManager() as session:
#         # Iterate over the countries and their banks
#         for country_code, banks in banks_data['banks'].items():
#             for bank in banks:
#                 # Check if the bank already exists in the database by name and country
#                 existing_bank = session.query(BankInformation).filter_by(name=bank['name'], country=country_code).first()
#
#                 # Load logo and illustration files if they exist
#                 logo_data = bank.get('logo', None)  # Check if logo exists
#                 illustration_data = bank.get('illustration', None) # Check if illustration exists
#
#                 if existing_bank:
#                     # Update the existing bank record
#                     existing_bank.supported = bank.get('supported', False)
#                     existing_bank.set_supported_file_formats(bank.get('supported_file_formats', ['unknown']))  # Update formats
#                     existing_bank.set_aliases(bank.get('aliases', []))  # Update aliases
#                     existing_bank.logo = logo_data if logo_data else existing_bank.logo  # Only update if logo exists
#                     existing_bank.illustration = illustration_data if illustration_data else existing_bank.illustration  # Only update if illustration exists
#                     existing_bank.updated_at = datetime.utcnow()
#                 else:
#                     # Insert a new bank record
#                     new_bank = BankInformation(
#                         name=bank['name'],
#                         supported=bank.get('supported', False),
#                         country=country_code,
#                         logo=logo_data,
#                         illustration=illustration_data,
#                         updated_at=datetime.utcnow()
#                     )
#                     new_bank.set_supported_file_formats(bank.get('supported_file_formats', ['unknown']))  # Set formats
#                     new_bank.set_aliases(bank.get('aliases', []))  # Set aliases
#                     session.add(new_bank)
#
#         session.commit()
#
#
#
#
# def main():
#     update_banks_from_yaml('../../assets/config/banks.yaml')
#
#
#
#
# if __name__ == '__main__':
#     main()
#
#
