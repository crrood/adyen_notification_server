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
        )

        # iterate through object and populate row data
        for column in Notification.__table__.columns:
            if column.name in item.keys():
                setattr(notification, column.name, item[column.name])

        # insert notification into list to be added to DB
        session.add(notification)

    # commit to DB
    session.commit()
    
    return notification.__repr__()

# pull all notifications from DB
def pull_all_notifications():
    return "a fuckload of notifications"

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

# respond to GET requests to confirm that the server is up
@app.route("/notification_server/notifications/", methods=["GET"])
def return_all_notifications():
    return app.response_class(["Hi there!"], 200)

# route notifications to DB
@app.route("/notification_server/notifications/", methods=["POST"])
def route_to_db():

    # get JSON object from request data
    json_data = request.get_json(force=True)

    # save to DB
    save_to_db(json_data)

    # send to DB
    return app.response_class(["[accepted]"], 200)

# display table HTML page
@app.route("/notification_server/view_table/", methods=["GET"])
def display_notification_table():
    with open("table.html", "r") as html_file:
        file_contents = html_file.read()
    return app.response_class([file_contents], 200)
