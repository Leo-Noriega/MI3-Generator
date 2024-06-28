import os

from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient

load_dotenv(find_dotenv())

DB_HOST = os.getenv('MONGO_HOST')
DB_PORT = os.getenv('MONGO_PORT')
DB_USER = os.getenv('MONGO_USER')
DB_PASSWORD = os.getenv('MONGO_PASS')
DB_NAME = os.getenv('MONGO_DB')

if not DB_USER or not DB_PASSWORD:
    url = f"mongodb://{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    url = f"mongodb://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?authSource={DB_NAME}"

client = MongoClient(url)
