import json
import os

import requests
import xmltodict
from dotenv import load_dotenv


def post_hist_perfiles(no_serie, tipo_var, tipo_dispo, tipo_perfil, fechaini, fechafin, json_perfiles):
    load_dotenv()

    sismedia_webservice = os.getenv("SISMEDIA_WEBSERVICE")
    sismedia_token = os.getenv("SISMEDIA_TOKEN")
    headers = {
        'Content-Type': 'application/soap+xml; charset=utf-8',
    }

    body = f"""<?xml version="1.0" encoding="utf-8"?>
    <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
      <soap12:Header>
        <oCabeceraSoapToken xmlns="http://localhost/Submedicionv2">
          <TokenAcceso>{sismedia_token}</TokenAcceso>
        </oCabeceraSoapToken>
      </soap12:Header>
      <soap12:Body>
        <HistPerfiles xmlns="http://localhost/Submedicionv2">
          <no_serie>{no_serie}</no_serie>
          <tipo_var>{tipo_var}</tipo_var>
          <tipo_dispo>{tipo_dispo}</tipo_dispo>
          <tipo_perfil>{tipo_perfil}</tipo_perfil>
          <fechaini>{fechaini}</fechaini>
          <fechafin>{fechaini}</fechafin>
          <json_perfiles>{json_perfiles}</json_perfiles>
        </HistPerfiles>
      </soap12:Body>
    </soap12:Envelope>
    """
    try:
        response = requests.post(sismedia_webservice, data=body, headers=headers)
        b = xmltodict.parse(response.content)
        c = b['soap:Envelope']['soap:Body']['HistPerfilesResponse']['HistPerfilesResult']['Code']
        desc_code_response = b['soap:Envelope']['soap:Body']['HistPerfilesResponse']['HistPerfilesResult']['Desc']
        result = b['soap:Envelope']['soap:Body']['HistPerfilesResponse']['json_perfiles']
        result = json.loads(result)
        # print(f"Datos registrados para el día {fechaini} con el código {c} y descripción {desc_code_response}")
        if desc_code_response == "No se pudo establecer comunicación con el dispositivo":
            return "Falló la comunicacíon con el dispositivo"
        elif "No se pudo establecer comunicación" in desc_code_response:
            return "Falló la comunicacíon con el dispositivo"
        elif desc_code_response == "Acceso no autorizado. Se requiere que vuelva a iniciar sesión":
            return "Acceso no autorizado"
        return {"code": c, "description": desc_code_response, "valores": result}
    except requests.exceptions.RequestException as e:
        return e
