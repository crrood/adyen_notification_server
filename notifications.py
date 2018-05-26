# utilities
import json, time
from urllib.request import Request, urlopen

# DB connection
# import sqlalchemy
# from sqlalchemy.orm import sessionmaker
# from schema.notifications import Notification

# Flask
from flask import Flask, Response, request, send_from_directory

# initialize routing
app = Flask(__name__)

# initialize DB connection
# engine = sqlalchemy.create_engine("postgresql+psycopg2://postgres:tgpli8sc2f@localhost:5432/postgres")
# Session = sessionmaker(bind=engine)

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

# save to a file to be read by the rss page
def save_to_rss_file(json_data):
     # pull list of notifications from JSON
    items = json_data["notificationItems"]

    # parse notifications
    for item in items:
        item = item["NotificationRequestItem"]

        # save notification to file for merchant account
        merchant_account = item["merchantAccountCode"]
        with open("notification_files/{}".format(merchant_account), "w") as file:
            file.write("data: {}".format(item))
            file.write("\n\n")

# serve static files
@app.route('/static_files/<path:path>')
def serve_files(path):
    return send_from_directory("static_files", path)

# respond to GET requests to confirm that the server is up
@app.route("/notification_server/notifications/", methods=["GET"])
def return_all_notifications():
    return app.response_class(["Hi there!"], 200)

# respond with event-stream encoded notification
# for a given merchant account
@app.route("/notification_server/notifications/<merchant_account>", methods=["GET"])
def return_latest_for_merchant(merchant_account):
    # load event to send from file
    with open("notification_files/{}".format(merchant_account), "r") as file:
        file_contents = file.read()

    # build response
    resp = Response(response=file_contents, mimetype="text/event-stream")
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Cache-Control"] = "no-cache"

    # send response
    return resp

# route notifications to DB
@app.route("/notification_server/notifications", methods=["POST"])
def incoming_notification():
    # get JSON object from request data
    json_data = request.get_json(force=True)

    # save to DB
    # save_to_db(json_data)

    # save to file to be read by rss feed
    save_to_rss_file(json_data)

    # send accepted response
    return app.response_class(["[accepted]"], 200)

# display table HTML page
@app.route("/notification_server/view_table/", methods=["GET"])
def display_notification_table():
    with open("table.html", "r") as html_file:
        file_contents = html_file.read()
    return app.response_class([file_contents], 200)
