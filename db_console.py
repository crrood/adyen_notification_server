import sys, csv, json
import code, readline

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

variables = globals().copy()
variables.update(locals())
shell = code.InteractiveConsole(variables)
shell.interact()
