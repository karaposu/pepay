from sqlalchemy import Column, Integer, DateTime, Numeric
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CommunitySize(Base):
    __tablename__ = 'community_size'
    
    id = Column(Integer, primary_key=True, autoincrement=True)

    value_date = Column(DateTime, nullable=False)
    fill_date = Column(DateTime, nullable=False)

    twitter = Column(Integer, nullable=True)
    reddit = Column(Integer, nullable=True)
    discord = Column(Integer, nullable=True)
    telegram = Column(Integer, nullable=True)
    
    price_in_usdt = Column(Numeric(20, 8), nullable=True)
    marcetcap = Column(Numeric(20, 8), nullable=True)