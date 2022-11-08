
from sqlalchemy import Column, Integer, Float
from database import Base

class Address(Base):
    __tablename__ = "address"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
