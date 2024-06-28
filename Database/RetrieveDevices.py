import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from dotenv import load_dotenv, find_dotenv

from Database.DbConnection import client

load_dotenv(find_dotenv())

DB_NAME = os.getenv("MONGO_DB")
DB = client[DB_NAME]
COLLECTION_NAME = os.getenv("MONGO_DEVICES_COLLECTION")
DB_COLLECTION = DB[COLLECTION_NAME]


def save_device_json(device):
    try:
        folder_path = Path('Devices')
        folder_path.mkdir(parents=True, exist_ok=True)
        file_path = folder_path / f'{device["no_serie"]}.json'
        with file_path.open('w') as f:
            json.dump({
                "device_id": device["device_id"],
                "no_serie": device["no_serie"],
                "pm_id": device.get("pm_id", "")
            }, f, indent=4)
    except Exception as e:
        print(f"Error saving JSON for {device['no_serie']}: {e}")


def retrive_devices():
    try:
        devices = list(DB_COLLECTION.find({"brand": "Sismedia-RT"}))
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(save_device_json, device) for device in devices]

        for future in as_completed(futures):
            future.result()

        print("Device retrieval completed.")
    except Exception as e:
        print(f"Error retrieving devices: {e}")
