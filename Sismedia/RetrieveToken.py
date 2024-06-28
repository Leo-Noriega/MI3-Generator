import os
from xml.parsers.expat import ExpatError

import requests
import xmltodict
from dotenv import load_dotenv, find_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv(find_dotenv())

# Variables de entorno para SISMEDIA
SISMEDIA_USER = os.getenv("SISMEDIA_USER")
SISMEDIA_PW = os.getenv("SISMEDIA_PASSWORD")
SISMEDIA_WEBSERVICE = os.getenv("SISMEDIA_WEBSERVICE")
MAX_TRIES = 3


def get_token_access(user, password, cont=0):
    headers = {'content-type': 'text/xml; charset=utf-8', 'SOAPAction': "http://localhost/Submedicionv2/GetTokenAccess"}

    body = f"""<?xml version="1.0" encoding="utf-8"?>
    <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
        <soap12:Header>
            <oCabeceraSoapAcceso xmlns="http://localhost/Submedicionv2">
                <Usuario>{user}</Usuario>
                <Password>{password}</Password>
            </oCabeceraSoapAcceso>
        </soap12:Header>
        <soap12:Body>
            <GetTokenAccess xmlns="http://localhost/Submedicionv2" />
        </soap12:Body>
    </soap12:Envelope>
    """
    try:
        response = requests.post(SISMEDIA_WEBSERVICE, data=body, headers=headers)
        response.raise_for_status()
        b = xmltodict.parse(response.content)
        c = b['soap:Envelope']['soap:Body']['GetTokenAccessResponse']['GetTokenAccessResult']['Token']
        return c
    except requests.exceptions.RequestException as e:
        print(f"RequestException: {e}")
        if cont < MAX_TRIES:
            return get_token_access(user, password, cont=cont + 1)
    except ExpatError as ex:
        print(f"ExpatError: {ex}")
    return None


def update_token_env():
    new_token = get_token_access(SISMEDIA_USER, SISMEDIA_PW)
    if not new_token:
        print("Failed to obtain new token")
        return

    os.environ["SISMEDIA_TOKEN"] = new_token
    print(f"New token: {new_token}")

    try:
        with open('.env', 'r') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading .env file: {e}")
        return

    token_updated = False
    for i, line in enumerate(lines):
        if line.startswith('SISMEDIA_TOKEN'):
            lines[i] = f'SISMEDIA_TOKEN={new_token}\n'
            token_updated = True
            break

    if not token_updated:
        lines.append(f'SISMEDIA_TOKEN={new_token}\n')

    try:
        with open('.env', 'w') as f:
            f.writelines(lines)
    except Exception as e:
        print(f"Error writing .env file: {e}")
