# utilities
import json, time
from urllib.request import Request, urlopen

# DB connection
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select
from sqlalchemy import desc
from schema.notifications import Notification

# Flask
from flask import Flask, Response, request, send_from_directory
app = Flask(__name__)

# Jinja
from jinja2 import Environment, PackageLoader
env = Environment(
    loader=PackageLoader("notifications", "templates")
)

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

# get rawData for range of notifications for given merchantAccount from DB
# the most recent notification isn't included, as it's stored in the file system
# returns an array
def get_range_from_db(merchant_account, first_notification, last_notification):
    session = Session()
    result = []
    for id, raw_data in session.query(Notification.id, Notification.rawData).\
            filter_by(merchantAccountCode=merchant_account).\
            order_by(desc(Notification.id))[first_notification : last_notification]:
        result.append(raw_data)

    return result

# get all notifications from DB
def get_all_notifications():
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

# show rss feed for merchant account
@app.route("/notification_server/notifications/view/<merchant_account>", methods=["GET"])
def render_rss_feed(merchant_account):
    # render jinja template with merchant account inserted
    template = env.get_template("rss_page.html")
    return template.render(merchant_account=merchant_account)

# respond to GET requests to confirm that the server is up
@app.route("/notification_server/", methods=["GET"])
def return_all_notifications():
    return app.response_class(["Hi there!"], 200)

# respond with most recent notification for a given merchant account
# reads from a file rather than the DB
# event-stream encoded for digestion by server-sent event listener
@app.route("/notification_server/notifications/<merchant_account>", methods=["GET"])
def return_latest(merchant_account):
    
    # load event to send from file
    try:
        with open("notification_files/{}".format(merchant_account), "r") as file:
            file_contents = file.read()

       # build response
        resp = Response(response=file_contents, mimetype="text/event-stream")
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Cache-Control"] = "no-cache"

        return resp

    except FileNotFoundError:
        return ""

# respond with most recent n notifications for a given merchant account
# returns array of json objects pulled from DB
@app.route("/notification_server/notifications/<string:merchant_account>/<int:first_notification_id>/<int:last_notification_id>", methods=["GET"])
def return_range_for_merchant(merchant_account, first_notification_id, last_notification_id):
    result = get_range_from_db(merchant_account, first_notification_id, last_notification_id)
    return Response("{}".format(result))

# handle incoming notifications
@app.route("/notification_server/notifications/", methods=["POST"])
def incoming_notification():
    # get JSON object from request data
    json_data = request.get_json(force=True)

    # save to DB
    save_to_db(json_data)

    # save to file to be read by rss feed
    save_to_rss_file(json_data)

    # send accepted response
    return app.response_class(["[accepted]"], 200)
