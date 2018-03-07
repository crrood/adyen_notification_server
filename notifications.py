# utilities
import json

# DB connection
import sqlalchemy
from schema_notification import Notification

# Flask
from flask import Flask, request

app = Flask(__name__)
engine = sqlalchemy.create_engine("postgresql+psycopg2://postgres:tgpli8sc2f@localhost:5432/postgres")

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

    
    return notification.__repr__()

# route notifications to DB
@app.route("/server/notifications/save", methods=["POST"])
def route_to_db():

    # get JSON object from request data
    json_data = request.get_json(force=True)

    # send to DB
    return app.response_class([save_to_db(json_data)], 200)
