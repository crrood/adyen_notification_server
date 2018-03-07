# utilities
import json

# DB connection
import sqlalchemy, psycopg2
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Boolean, Float, Integer

engine = sqlalchemy.create_engine("postgresql+psycopg2://postgres:tgpli8sc2f@localhost:5432/postgres")
Base = declarative_base()

# Flask
from flask import Flask, request

app = Flask(__name__)

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

# save notifications to DB
def save_to_db(json_data):
    
    # pull list of notifications from JSON
    items = json_data["notificationItems"]

    # parse notifications for entry into DB
    for item in items:
        item = item["NotificationRequestItem"]
        #data_to_insert = {}
        notification = Notification(rawData=item)
        for column in Notification.__table__.columns:
            if column.name in item.keys():
                #data_to_insert[column] = item[column]
                setattr(notification, column.name, item[column.name])

        # insert notification into DB
    #notification.psp_reference = type(item)
    #notification.merchant_account = item["merchant_account"]
    return notification.__repr__()

# route notifications to DB
@app.route("/server/notifications/save", methods=["POST"])
def route_to_db():

    # get JSON object from request data
    json_data = request.get_json(force=True)

    # send to DB
    return app.response_class([save_to_db(json_data)], 200)
