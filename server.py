# server.py
import os
from dotenv import load_dotenv
import requests
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
from typing import Optional
from app import reverse_text


mcp = FastMCP("nps-info-server")

nps_api_base_url = "https://developer.nps.gov/api/v1"

if not os.getenv("NPS_API_KEY"):
    load_dotenv()
NPS_API_KEY = os.getenv("NPS_API_KEY")


class ParkModelArgs(BaseModel):
    park_code: Optional[str] = Field(description="Park code from NPS website")
    state_code: Optional[str] = Field(description="US state where the park is addresed")
    search_term: Optional[str] = Field(description="Term to search in the API output")

    

@mcp.tool()
def get_park(args: ParkModelArgs):
    """API request to NPS website to get retrieve data about national parks (addresses, contacts, description, hours of operation, etc.)"""
    params = {
        "parkCode": args.park_code,
        "stateCode": args.state_code,
        "q": args.search_term,
        "api_key": os.getenv("NPS_API_KEY")
    }
    headers = {
        "accept": "application/json"
    }
    client_url = nps_api_base_url + "/parks"
    
    try:
        response = requests.get(client_url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        return {"error": str(err)}


@mcp.tool()
async def reverse_text_tool(text: str) -> str:
    """
    MCP server to reverse a text
    """
    return reverse_text(text)

if __name__ == "__main__":
    mcp.run(transport="stdio")