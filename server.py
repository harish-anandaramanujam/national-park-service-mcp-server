# server.py
import os
from dotenv import load_dotenv
import requests
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
from typing import Optional
import src.api_utils
from src.models import ParkModelArgs

mcp = FastMCP("nps-info-server")

nps_api_base_url = "https://developer.nps.gov/api/v1"

if not os.getenv("NPS_API_KEY"):
    load_dotenv()
NPS_API_KEY = os.getenv("NPS_API_KEY")


@mcp.tool()
async def get_park_tool(args: ParkModelArgs):
    """Tool that could retrieve 
    data about national parks (addresses, contacts, description, 
    hours of operation, etc.)"""
    
    client_url = nps_api_base_url + "/parks"

    return await src.api_utils.nps_get(args, client_url)

@mcp.tool()
async def get_passport_stamp_locations_tool(args: ParkModelArgs):
    """Tool that could get retrieve locations (see "campgrounds",
    "places", and "visitorcenters") that have national park
    passport stamps."""
    
    client_url = nps_api_base_url + "/passportstamplocations"

    return await src.api_utils.nps_get(args, client_url)


@mcp.tool()
async def get_alerts_tool(args: ParkModelArgs):
    """Tool that could Retrieve alerts 
    (danger, closure, caution, and information) 
    posted by parks."""
    
    client_url = nps_api_base_url + "/alerts"

    return await src.api_utils.nps_get(args, client_url)

@mcp.tool()
async def get_articles_tool(args: ParkModelArgs):
    """Tool that could Retrieve articles created by national parks 
    and other NPS entities. 
    (See "people" and "places" below for other specific article types.)"""
    
    client_url = nps_api_base_url + "/articles"

    return await src.api_utils.nps_get(args, client_url)


if __name__ == "__main__":
    mcp.run(transport="stdio")