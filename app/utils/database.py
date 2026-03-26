from pymongo import MongoClient
import certifi

import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

import logging
from app.utils.logger import get_logger

logger = get_logger(__name__)

logger.info('mongo started')

client = MongoClient(DATABASE_URL, tlsCAFile=certifi.where())

logger.info('mongo client created')

def get_database():

    db = client['news_analysis']

    return db

