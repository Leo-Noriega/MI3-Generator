import json
import math
import os
from datetime import datetime, timedelta
from multiprocessing import Pool, cpu_count
from pathlib import Path

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

data_types = ['Energia Activa', 'Voltaje', 'Corriente', 'Factor de potencia', 'Potencia activa']


def get_apparent_power(active_power, power_factor):
    active_power = float(active_power) if active_power is not None else None
    power_factor = float(power_factor) if power_factor is not None else None

    if (
            active_power is not None
            and power_factor is not None
            and power_factor != 0
            and not math.isnan(active_power)
            and not math.isnan(power_factor)
    ):
        try:
            return active_power / power_factor
        except ZeroDivisionError:
            print("No se puede dividir entre 0")
            return None
        except TypeError:
            print("Tipo de variable no válida")
            return None
    else:
        return None


def get_reactive_power(apparent_power, active_power):
    if apparent_power is not None and active_power is not None:
        try:
            tmp = pow(apparent_power, 2) - pow(active_power, 2)
            return math.sqrt(tmp) if tmp >= 0 else None
        except TypeError:
            print(f"Fallo en la operación: {apparent_power}, {active_power}")
            return None
    else:
        return None


def replace_nan_with_null(value):
    if isinstance(value, float) and math.isnan(value):
        return None
    elif isinstance(value, str) and value.lower() == "nan":
        return None
    else:
        return value


def build_unified_json(no_serie, date):
    data = {}
    for data_type in range(1, 6):
        file_path = os.path.join("Data", no_serie, date, f'{data_type}-{no_serie}-{date}.json')

        if not os.path.exists(file_path):
            print(f"Archivo no encontrado: {file_path}")
            continue

        with open(file_path, 'r') as f:
            json_data = json.load(f)

        for fase in json_data['valores']:
            for i, value in enumerate(fase['Valores']):
                time = (datetime(2024, 4, 1, 0, 5) + timedelta(minutes=5 * i)).time().isoformat()

                if time not in data:
                    data[time] = {}

                data[time][f'{data_types[data_type - 1]} Fase {fase["FaseCanal"]}'] = replace_nan_with_null(value)

    for time, values in data.items():
        for fase in json_data['valores']:
            active_power = values.get(f'Potencia activa Fase {fase["FaseCanal"]}')
            power_factor = values.get(f'Factor de potencia Fase {fase["FaseCanal"]}')

            apparent_power = get_apparent_power(active_power, power_factor)
            reactive_power = get_reactive_power(apparent_power, active_power)

            values[f'Potencia aparente Fase {fase["FaseCanal"]}'] = replace_nan_with_null(apparent_power)
            values[f'Potencia reactiva Fase {fase["FaseCanal"]}'] = replace_nan_with_null(reactive_power)

    output_path = os.path.join("Data", no_serie, date, f'{no_serie}-{date}-FINAL.json')
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=4)


def process_device(no_serie):
    for date_folder in os.listdir(os.path.join("Data", no_serie)):
        build_unified_json(no_serie, date_folder)


def get_unified_jsons():
    devices_folder = Path('/Users/noriega/Documents/Projects/generatorMI3/Devices')
    devices_data = []

    for device_file in devices_folder.glob('*.json'):
        with device_file.open('r') as f:
            device_data = json.load(f)
            devices_data.append(device_data['no_serie'])

    with Pool(processes=cpu_count()) as pool:
        pool.map(process_device, devices_data)

    print("All jsons have been unified")
