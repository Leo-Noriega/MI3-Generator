import json
import os
from datetime import datetime

import numpy as np


def get_device_id_map(directory):
    device_id_map = {}
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            file_path = os.path.join(directory, filename)
            with open(file_path, "r") as f:
                data = json.load(f)
            device_id = data.get("device_id")
            no_serie = data.get("no_serie")
            pm_id = data.get("pm_id")
            if device_id and no_serie:
                device_id_map[no_serie] = {
                    "device_id": device_id,
                    "pm_id": pm_id
                }
    return device_id_map


def process_json_file(file_path, device_id_map):
    with open(file_path, "r") as f:
        data = json.load(f)

    file_name = os.path.basename(file_path)
    parts = file_name.split("-")
    no_serie = parts[0]
    date_str = "-".join(parts[1:4])

    device_info = device_id_map.get(no_serie)
    if not device_info:
        raise ValueError(f"No se encontró información del dispositivo para el número de serie {no_serie}")

    device_id = device_info["device_id"]
    pm_id = device_info["pm_id"]

    db_data = []
    index = 0
    for time, values in data.items():
        time_obj = datetime.strptime(f"{date_str} {time}", "%Y-%m-%d %H:%M:%S")
        db_record = {
            "device_id": device_id,
            "no_serie": no_serie,
            "pm_id": pm_id,
            "date": {"$date": time_obj.isoformat() + ".000Z"},
            "index": index,
            "values": [None] * 40,
        }

        for fase in range(1, 3):
            db_record["values"][fase - 1] = values.get(f"Corriente Fase {fase}", None)
            db_record["values"][fase + 3] = values.get(f"Voltaje Fase {fase}", None)
            db_record["values"][fase + 11] = values.get(f"Potencia activa Fase {fase}", None)
            db_record["values"][fase + 15] = values.get(f"Potencia reactiva Fase {fase}", None)
            db_record["values"][fase + 19] = values.get(f"Potencia aparente Fase {fase}", None)
            db_record["values"][fase + 23] = values.get(f"Factor de potencia Fase {fase}", None)
            db_record["values"][fase + 31] = values.get(f"Energia Activa Fase {fase}", None)

        for i in range(36):
            try:
                if db_record["values"][i] is not None:
                    db_record["values"][i] = float(db_record["values"][i])
            except ValueError:
                db_record["values"][i] = None

        db_record["values"] = [None if (v is None or np.isnan(v)) else v for v in db_record["values"]]

        db_record["values"][3] = sum([v for v in db_record["values"][0:3] if v is not None])
        db_record["values"][7] = sum([v for v in db_record["values"][4:7] if v is not None]) / 3
        db_record["values"][15] = sum([v for v in db_record["values"][12:15] if v is not None])
        db_record["values"][19] = sum([v for v in db_record["values"][16:19] if v is not None])
        db_record["values"][23] = sum([v for v in db_record["values"][20:23] if v is not None])
        db_record["values"][27] = sum([v for v in db_record["values"][24:27] if v is not None]) / 3
        db_record["values"][35] = sum([v for v in db_record["values"][32:35] if v is not None])

        db_data.append(db_record)
        index += 1

    return db_data


def process_all_json_files():
    data_directory = "/Users/noriega/Documents/Projects/generatorMI3/Data"
    devices_directory = "/Users/noriega/Documents/Projects/generatorMI3/Devices"

    device_id_map = get_device_id_map(devices_directory)

    for root, dirs, files in os.walk(data_directory):
        for file in files:
            if file.endswith("-FINAL.json"):
                file_path = os.path.join(root, file)
                db_data = process_json_file(file_path, device_id_map)

                file_name = os.path.splitext(file)[0]
                parts = file_name.split("-")
                no_serie = parts[0]
                date_str = "-".join(parts[1:4])

                output_dir = os.path.join("Mongo", no_serie)
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, f"{no_serie}-{date_str}.json")

                with open(output_path, "w") as f:
                    json.dump(db_data, f, indent=4)

    print("Archivos JSON generados en la estructura de carpetas correspondiente.")
