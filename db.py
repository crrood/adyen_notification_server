import sys, csv, json

# DB connection
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from schema.notifications import Notification

# initialize engine
engine = sqlalchemy.create_engine("postgresql+psycopg2://postgres:tgpli8sc2f@localhost:5432/postgres")
Session = sessionmaker(bind=engine)

if sys.argv[1] == "reset":

    # remove existing data and
    # add schema to DB
    Notification.__table__.drop(engine, checkfirst=True)
    Notification.__table__.create(engine)

elif sys.argv[1] == "migrate":

    # add data from csv file
    with open("db_dump.csv") as csvfile:
        reader = csv.DictReader(csvfile)

        # create a new DB session
        session = Session()

        # parse notifications for entry into DB
        for row in reader:

            # create new notification object to insert into DB
            notification = Notification()

            # iterate through object and populate row data
            for column in Notification.__table__.columns:
                if column.name in row.keys():
                    setattr(notification, column.name, row[column.name])

            # imperfect mappings
            json_data = json.loads(row["data"])["notificationItems"][0]["NotificationRequestItem"]
            notification.rawData = json_data
            notification.merchantAccountCode = json_data["merchantAccountCode"]
            notification.eventCode = json_data["eventCode"]
            notification.success = json_data["success"].lower() == "true"

            # insert notification into list to be added to DB
            session.add(notification)

        # commit to DB
        session.commit()
