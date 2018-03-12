# utilities
import json, time
from urllib.request import Request, urlopen

# DB connection
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from schema.notifications import Notification

# Flask
from flask import Flask, request

# initialize routing
app = Flask(__name__)

# initialize DB connection
engine = sqlalchemy.create_engine("postgresql+psycopg2://postgres:tgpli8sc2f@localhost:5432/postgres")
Session = sessionmaker(bind=engine)

# save notifications to DB
def save_to_db(json_data):
    
    # pull list of notifications from JSON
    items = json_data["notificationItems"]

    # create a new DB session
    session = Session()

    # parse notifications for entry into DB
    for item in items:
        item = item["NotificationRequestItem"]

        # create new notification object to insert into DB
        notification = Notification(
            rawData=item,
            timestamp=time.time()
        ))

        # iterate through object and populate row data
        for column in Notification.__table__.columns:
            if column.name in item.keys():
                setattr(notification, column.name, item[column.name])

        # insert notification into list to be added to DB
        session.add(notification)

    # commit to DB
    session.commit()
    
    return notification.__repr__()

# post notification to Mattermost channel
def send_to_mattermost(json_data):

    # set values to be re-used
    MATTERMOST_URL = "https://mattermost.is.adyen.com/hooks/uz747icn5ig13bx8o5kw9ik5ya"
    headers = { "Content-type": "application/json" }

     # pull list of notifications from JSON
    items = json_data["notificationItems"]

    # parse notifications for forwarding
    for item in items:
        item = item["NotificationRequestItem"]


        # build request object
        mattermost_data = {
            "username": item["merchantAccountCode"],
            "text": json.dumps(item)
        }

        # send request
        #request = Request(MATTERMOST_URL, json.dumps(mattermost_data).encode("UTF8"), headers)
        request = Request(MATTERMOST_URL, '{"text": "Testing..."}'.encode("UTF8"), headers)
        urlopen(request)

    return "sent to mattermost successfully"

# route notifications to DB
@app.route("/server/notifications/save", methods=["POST"])
def route_to_db():

    # get JSON object from request data
    json_data = request.get_json(force=True)

    # send to DB
    return app.response_class([save_to_db(json_data)], 200)
