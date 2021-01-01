from flask_sqlalchemy import SQLAlchemy
import os
import pymongo
from dotenv import load_dotenv
load_dotenv()

# postgres db
db = SQLAlchemy()


# mongo db
client = pymongo.MongoClient(os.environ['MONGODB_URL'])
mongodb = client.planr
