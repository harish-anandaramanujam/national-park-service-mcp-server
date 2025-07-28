import os
from dotenv import load_dotenv
import requests
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
from typing import Optional

load_dotenv(override=True)

mcp = FastMCP("nps-info-server")

nps_api_base_url = "https://developer.nps.gov/api/v1"


class ParkModelArgs(BaseModel):
    park_code: Optional[str] = Field(description="Park code from NPS website")
    state_code: Optional[str] = Field(description="US state where the park is addresed")
    search_term: Optional[str] = Field(description="Term to search in the API output")

    

@mcp.tool()
def get_park(args: ParkModelArgs):
    """API request to NPS website to get park activites"""
    params = {
        "parkCode": args.park_code,
        "stateCode": args.state_code,
        "q": args.search_term,
        "api_key": os.getenv("NPS_API_KEY")
    }
    headers = {
        "accept": "application/json"
    }
    park_url = nps_api_base_url + "/parks"
    
    try:
        response = requests.get(park_url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        return {"error": str(err)}


if __name__ == "__main__":
    mcp.run(transport="stdio")


