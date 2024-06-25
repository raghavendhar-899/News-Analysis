from pymongo import MongoClient
import certifi

import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')


print('mongo started')

client = MongoClient(DATABASE_URL, tlsCAFile=certifi.where())

print('mongo client created')

def get_database():

    db = client['news_analysis']

    return db

