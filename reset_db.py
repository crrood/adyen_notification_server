# DB connection
import sqlalchemy
from schema_notification import Notification

# initialize engine
engine = sqlalchemy.create_engine("postgresql+psycopg2://postgres:tgpli8sc2f@localhost:5432/postgres")

# add schema to DB
Notification.__table__.drop(engine, checkfirst=True)
Notification.__table__.create(engine)
