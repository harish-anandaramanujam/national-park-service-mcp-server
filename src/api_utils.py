import os
import requests
import mcp
from src.models import ParkModelArgs, GeneralModelArgs

async def nps_get_park(args: ParkModelArgs, client_url):
    params = {
        "parkCode": args.park_code,
        "stateCode": args.state_code,
        "q": args.search_term,
        "api_key": os.getenv("NPS_API_KEY")
    }
    headers = {
        "accept": "application/json"
    }
    
    try:
        response = requests.get(client_url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        return {"error": str(err)}


async def nps_get_general(args: GeneralModelArgs, client_url):
    params = {
        "id": args.id,
        "q": args.search_term,
        "api_key": os.getenv("NPS_API_KEY")
    }
    headers = {
        "accept": "application/json"
    }
    
    try:
        response = requests.get(client_url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        return {"error": str(err)}

async def nps_get_map_metadata(args: GeneralModelArgs, client_url):
    params = {
        "parkCode": args.park_code
    }
    headers = {
        "accept": "application/json"
    }
    
    client_url = client_url + args.park_code

    try:
        response = requests.get(client_url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        return {"error": str(err)}