# DB connection
import sqlalchemy
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Boolean, Float, Integer

engine = sqlalchemy.create_engine("postgresql+psycopg2://postgres:tgpli8sc2f@localhost:5432/postgres")
Base = declarative_base()

# create DB Declaratives
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    rawData = Column(JSONB)
    merchantAccountCode = Column(String(25))
    pspReference = Column(String(50))
    merchantReference = Column(String(75))
    timestamp = Column(Float)
    eventDate = Column(String(25))
    eventCode = Column(String(25))
    success = Column(Boolean)
    reason = Column(String(200))
    paymentMethod = Column(String(20))
    originalReference = Column(String)

    def __repr__(self):
        attributes = [field for field in dir(self) if field[0] != "_"]
        return str(["{}: {}".format(field, getattr(self, field)) for field in attributes])
