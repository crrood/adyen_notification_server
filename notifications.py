# utilities
import time, re, configparser
from urllib.request import Request, urlopen

# DB connection
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select
from sqlalchemy import desc, or_

# Migrations
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Flask
from flask import Flask, Response, request, send_from_directory
from flask_cors import CORS
from werkzeug.datastructures import Headers

# socketIO
from flask_socketio import SocketIO, emit

# Jinja
from jinja2 import Environment, PackageLoader
env = Environment(
    loader=PackageLoader("notifications", "templates")
)

parser = configparser.ConfigParser()
parser.read("config.ini")
config = parser["config"]

# set environment
# due to legacy the production environment is blank
ENV = config["env"]
if ENV == "PROD":
    SERVER_ROOT = "/notification_server"
else:
    SERVER_ROOT = "/notification_server_{}".format(config["env"])

# initialize flask app
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, path=f"{SERVER_ROOT}/socket.io")

# initialize DB connection
# username / password are in credentials.txt on line 1 and 2
with open("credentials.txt", "r") as credentials_file:
    username = credentials_file.readline().strip()
    password = credentials_file.readline().strip()
db_url = "postgresql+psycopg2://{}:{}@localhost:5432/postgres".format(username, password)
engine = sqlalchemy.create_engine(db_url)
Session = sessionmaker(bind=engine)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# create DB Declaratives
class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    rawData = db.Column(db.String(10000))
    merchantAccountCode = db.Column(db.String(75))
    pspReference = db.Column(db.String(100))
    merchantReference = db.Column(db.String(100))
    timestamp = db.Column(db.Float)
    eventDate = db.Column(db.String(25))
    eventCode = db.Column(db.String(25))
    success = db.Column(db.Boolean)
    reason = db.Column(db.String(300))
    paymentMethod = db.Column(db.String(100))
    originalReference = db.Column(db.String(100))

    def __repr__(self):
        attributes = [field for field in dir(self) if field[0] != "_"]
        return str(["{}: {}".format(field, getattr(self, field)) for field in attributes])

# remove apostrophes from raw data
def sanitize_response(raw_data):
    raw_data = re.sub(r"([a-zA-Z])'([a-zA-Z])", "\g<1>\g<2>", raw_data)
    raw_data = raw_data.replace('"', "'")
    return raw_data

# save notifications to DB
def save_to_db(json_data):
    # create a new DB session
    session = Session()

    # create new notification object to insert into DB
    notification = Notification(
        rawData=str(json_data),
        timestamp=time.time()
    )

    # iterate through object and populate row data
    for column in Notification.__table__.columns:
        if column.name in json_data.keys():
            formatted_value = json_data[column.name]
            if formatted_value.lower() == "false":
                formatted_value = False
            elif formatted_value.lower() == "true":
                formatted_value = True
            setattr(notification, column.name, formatted_value)

    # insert notification into list to be added to DB
    session.add(notification)

    # commit to DB
    session.commit()

    return notification.__repr__()

# save to a file to be read by the feed page
def save_to_file(json_data):
    # save notification to file for merchant account
    if "merchantAccountCode" in json_data.keys():
        merchant_account = json_data["merchantAccountCode"]
    else:
        merchant_account = config["default_merchant_account"]

    # save to file
    with open("notification_files/{}".format(merchant_account), "w") as file:
        file.write(str(json_data))

    # notify listeners
    socketio.emit("notification_available", {"merchantAccount": merchant_account, "notificationData": str(json_data)}, broadcast=True)

# get rawData for range of notifications for given merchantAccount from DB
# note the most recent notification isn't included, as it's stored in the file system for faster access
# returns an array
def get_range_from_db(merchant_account, first_notification, last_notification):
    session = Session()
    response = []

    # query DB
    results = session.query(Notification.id, Notification.rawData).\
        filter_by(merchantAccountCode=merchant_account).\
        order_by(desc(Notification.id))

    # put results into array
    last_notification = min(results.count() - 1, last_notification)
    for id, raw_data in results[first_notification : last_notification]:

        # get rid of apostrophes within fields
        raw_data = sanitize_response(raw_data)
        response.append(raw_data)

    return response

# get all notifications which match a PSP reference
def get_all_by_psp_reference(psp_reference):
    session = Session()
    response = []

    # query DB
    results = session.query(Notification.id, Notification.rawData).\
        filter(or_(Notification.pspReference == psp_reference, Notification.originalReference == psp_reference)).\
        order_by(desc(Notification.id))

    # put results into array
    for id, raw_data in results:

        # get rid of apostrophes within fields
        raw_data = sanitize_response(raw_data)
        response.append(raw_data)

    return response

# serve static files
@app.route(f'{SERVER_ROOT}/static_files/<path:path>')
def serve_files(path):
    return send_from_directory("static_files", path)

# show HTML page for notification feed
# generates a template based on merchant account in URL
@app.route(f"{SERVER_ROOT}/notifications/view/<merchant_account>", methods=["GET"])
def render_feed(merchant_account):
    # render jinja template with merchant account inserted
    template = env.get_template("notification_feed.html")
    return template.render(merchant_account=merchant_account, server_root=SERVER_ROOT)

# show HTML page for search by PSP reference
@app.route(f"{SERVER_ROOT}/notifications/view/search/<psp_reference>", methods=["GET"])
def render_search_results(psp_reference):
    # render jinja template with search results
    template = env.get_template("search_results.html")
    return template.render(psp_reference=psp_reference, server_root=SERVER_ROOT)

# respond to GET requests to confirm that the server is up
@app.route(f"{SERVER_ROOT}/", methods=["GET"])
def ping():
    return app.response_class(["Hi there!"], 200)

# load json from a file
def get_notification_from_file(merchant_account):
    with open("notification_files/{}".format(merchant_account), "r") as file:
        return sanitize_response(file.read())

# respond with most recent notification for a given merchant account
# reads from a file rather than the DB
@app.route(f"{SERVER_ROOT}/notifications/<merchant_account>", methods=["GET"])
def return_latest_via_http(merchant_account):
    return Response(get_notification_from_file(merchant_account),
        mimetype="text/json",
        headers=Headers([
            ("Access-Control-Allow-Origin", "roodberry.duckdns.org,www.roodvibes.com"),
            ("Cache-Control", "no-cache"),
            ("Connection", "keep-alive")
        ])
    )

# respond with notifications from n to m for a given merchant
# with n=0 being the latest entry
# returns array of json objects pulled from DB
@app.route(f"{SERVER_ROOT}/notifications/<string:merchant_account>/<int:first_notification_id>/<int:last_notification_id>", methods=["GET"])
def return_range_for_merchant(merchant_account, first_notification_id, last_notification_id):
    result = get_range_from_db(merchant_account, first_notification_id, last_notification_id)
    return Response("{}".format(result))

# return all notifications which match a given PSP reference
@app.route(f"{SERVER_ROOT}/notifications/search/<string:psp_reference>", methods=["GET"])
def return_by_psp_reference(psp_reference):
    result = get_all_by_psp_reference(psp_reference)
    return Response("{}".format(result))

# handle incoming notifications
@app.route(f"{SERVER_ROOT}/notifications/", methods=["POST"])
def incoming_notification():
    # get JSON object from request data
    json_data = request.get_json(force=True)

    # parse notification JSON
    # PSP notifications come in an array called "notificationItems"
    # but Marketpay notifications do not
    if "notificationItems" in json_data.keys():
        # iterate through list of notifications
        items = json_data["notificationItems"]

        for item in items:
            item = item["NotificationRequestItem"]

            # save to DB
            save_to_db(json_data)

            # save to file to be read by feed
            save_to_file(json_data)

    else:
        # save to DB
        save_to_db(json_data)

        # save to file to be read by feed
        save_to_file(json_data)

    # send accepted response
    return app.response_class(["[accepted]"], 200)

# serve static files
@app.route(f"{SERVER_ROOT}/static/<path:path>", methods=["GET"])
def serve_static_files(path):
    return send_from_directory("static", path)

@socketio.on("request_latest")
def return_latest_via_socket(data):
    emit("notification_avilable", {
        "merchantAccount": data["merchantAccount"],
        "notificationData": get_notification_from_file(data["merchantAccount"])
    })
    return get_notification_from_file(data["merchantAccount"])

@socketio.on("ping")
def pong(data):
    return data
