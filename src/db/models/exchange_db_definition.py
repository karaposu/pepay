# db/models/exchange_db_models.py


from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text, ForeignKey


from sqlalchemy.types import JSON
from sqlalchemy import LargeBinary, String
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime
from werkzeug.security import generate_password_hash
from sqlalchemy import Boolean
from sqlalchemy import Column, Integer, Float, Date, String, UniqueConstraint, ForeignKey, DateTime
Base = declarative_base()



class HistoricalCurrencyRates(Base):
    __tablename__ = "historical_currency_rates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    currency = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    rate_to_usd = Column(Float, nullable=False)  # Exchange rate to USD
    usd_to_gold_rate = Column(Float, nullable=False)  # Exchange rate to Gold
    usd_to_chf_rate = Column(Float, nullable=False)  # Exchange rate to CHF (Swiss Franc)

    # Ensuring that each currency and date pair is unique
    __table_args__ = (UniqueConstraint('currency', 'date', name='_currency_date_uc'),)

    def __repr__(self):
        return f"<HistoricalCurrencyRates(currency={self.currency}, date={self.date}, usd={self.exchange_rate_to_dollar}, gold={self.exchange_rate_to_gold}, chf={self.exchange_rate_to_chf})>"



engine = create_engine('sqlite:///mass_exchange_rate.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
