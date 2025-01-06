from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class AudiR8Sale(Base):
    __tablename__ = 'r8_sales'
    
    id = Column(Integer, primary_key=True)
    listing_name = Column(String)
    sale_price = Column(Float)
    sale_date = Column(DateTime)
    year = Column(Integer)
    is_manual = Column(Boolean)
    is_v10 = Column(Boolean)
    mileage = Column(Integer)
    created_at = Column(DateTime)