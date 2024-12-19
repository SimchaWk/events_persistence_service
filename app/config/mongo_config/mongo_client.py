from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv(verbose=True)

mongo_client = MongoClient(os.environ['MONGO_URL'])

mongo_db = mongo_client[os.environ['MONGO_DB_NAME']]

terror_events_collection = mongo_db['terror_events']
