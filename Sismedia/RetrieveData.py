import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv, find_dotenv

from Sismedia.HistoricalProfiles import post_hist_perfiles

# Cargar las variables de entorno desde el archivo .env
load_dotenv(find_dotenv())
START_DATE = os.getenv("START_DATE")
END_DATE = os.getenv("END_DATE")


def process_device(no_serie, tipo_var, tipo_dispo, tipo_perfil, fechaini, fechafin, json_perfiles):
    try:
        response = post_hist_perfiles(no_serie, tipo_var, tipo_dispo, tipo_perfil, fechaini, fechafin, json_perfiles)
        output_folder = Path(f'Data/{no_serie}/{fechaini}')
        output_folder.mkdir(parents=True, exist_ok=True)
        output_file = output_folder / f'{tipo_var}-{no_serie}-{fechaini}.json'
        with output_file.open('w') as f_out:
            json.dump(response, f_out, indent=4)
        # print(f"Procesado: {tipo_var}-{no_serie}-{fechaini}")
    except Exception as e:
        print(f"Error en {tipo_var}-{no_serie}-{fechaini}: {e}")


def process_devices():
    tipo_dispo = "2"
    tipo_perfil = "1"
    json_perfiles = ""

    start_date = datetime.strptime(START_DATE, "%Y-%m-%d")
    end_date = datetime.strptime(END_DATE, "%Y-%m-%d")

    devices_folder = Path('Devices')

    futures = []
    with ThreadPoolExecutor(max_workers=10) as executor:  # ajusta según tu necesidad
        for device_file in devices_folder.glob('*.json'):
            with device_file.open('r') as f:
                device_data = json.load(f)
                no_serie = device_data['no_serie']
                for tipo_var in range(1, 6):
                    for i in range((end_date - start_date).days + 1):
                        day = start_date + timedelta(days=i)
                        fechaini = day.strftime("%Y-%m-%d")
                        fechafin = day.strftime("%Y-%m-%d")
                        futures.append(
                            executor.submit(process_device, no_serie, tipo_var, tipo_dispo, tipo_perfil, fechaini,
                                            fechafin, json_perfiles)
                        )

    for future in as_completed(futures):
        future.result()

    print(f"Data collected from {START_DATE} to {END_DATE}")
