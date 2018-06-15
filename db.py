import sys, csv, json

# DB connection
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from schema.notifications import Notification

# initialize engine
with open("credentials.txt", "r") as credentials_file:
    username = credentials_file.readline().strip()
    password = credentials_file.readline().strip()
engine = sqlalchemy.create_engine("postgresql+psycopg2://{}:{}@localhost:5432/postgres".format(username, password))
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
            notification.timestamp = float(notification.timestamp)
            notification.success = notification.success.lower() == "true"

            # insert notification into list to be added to DB
            session.add(notification)

        # commit to DB
        session.commit()

elif sys.argv[1] == "dump":
    
    # create a session
    session = Session()
    
    # load all notifications
    notifications = session.query(Notification)

    # dump to csv file
    with open("db_dump.csv", "w") as output_file:

        # write headers
        for column in Notification.__table__.columns:
            output_file.write("{},".format(column.name))
        output_file.write("\n")

        # write contents of Notification table
        for notification in session.query(Notification):
            for column in Notification.__table__.columns:
                output_file.write('"{}",'.format(str(getattr(notification, column.name).replace("'", ""))))
            output_file.write("\n")
