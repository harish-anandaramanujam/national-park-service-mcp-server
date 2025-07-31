import os
import requests
import mcp
from src.models import ParkModelArgs

async def get_park(args: ParkModelArgs, client_url):
    """API request to NPS website to retrieve data about national parks (addresses, contacts, description, hours of operation, etc.)"""
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