import datetime
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient

# Cargar las variables de entorno
load_dotenv(find_dotenv())

# Conectar a la base de datos MongoDB
DB_NAME = os.getenv("MONGO_DB")
DATA_COLLECTION_NAME = os.getenv("MONGO_DATA_COLLECTION")

client = MongoClient(os.getenv("MONGO_URI"))
db = client[DB_NAME]
data_collection = db[DATA_COLLECTION_NAME]


def convert_dates(data):
    if isinstance(data, list):
        for item in data:
            if "date" in item and isinstance(item["date"], str):
                item["date"] = datetime.datetime.strptime(item["date"], "%Y-%m-%dT%H:%M:%SZ")
            if "last_updated" in item and isinstance(item["last_updated"], str):
                item["last_updated"] = datetime.datetime.strptime(item["last_updated"], "%Y-%m-%dT%H:%M:%SZ")
    else:
        if "date" in data and isinstance(data["date"], str):
            data["date"] = datetime.datetime.strptime(data["date"], "%Y-%m-%dT%H:%M:%SZ")
        if "last_updated" in data and isinstance(data["last_updated"], str):
            data["last_updated"] = datetime.datetime.strptime(data["last_updated"], "%Y-%m-%dT%H:%M:%SZ")
    return data


def insert_json_file(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)
        data = convert_dates(data)
        if isinstance(data, list):
            data_collection.insert_many(data)
        else:
            data_collection.insert_one(data)


def insert_json_files(directory):
    files_to_insert = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                files_to_insert.append(file_path)

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(insert_json_file, file_path) for file_path in files_to_insert]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error inserting file: {e}")


def insert_data():
    mongo_directory = "/Users/noriega/Documents/Projects/generatorMI3/Mongo"
    insert_json_files(mongo_directory)
    print(f"Inserción de archivos JSON en la base de datos '{DB_NAME}' completada.")
