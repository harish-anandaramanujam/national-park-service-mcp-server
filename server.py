# server.py
import os
from dotenv import load_dotenv
import requests
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
from typing import Optional
import src.api_utils
from src.models import ParkModelArgs, GeneralModelArgs

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

    return await src.api_utils.nps_get_park(args, client_url)

@mcp.tool()
async def get_passport_stamp_locations_tool(args: ParkModelArgs):
    """Tool that could get retrieve locations (see "campgrounds",
    "places", and "visitorcenters") that have national park
    passport stamps."""
    
    client_url = nps_api_base_url + "/passportstamplocations"

    return await src.api_utils.nps_get_park(args, client_url)


@mcp.tool()
async def get_alerts_tool(args: ParkModelArgs):
    """Tool that could Retrieve alerts 
    (danger, closure, caution, and information) 
    posted by parks."""
    
    client_url = nps_api_base_url + "/alerts"

    return await src.api_utils.nps_get_park(args, client_url)

@mcp.tool()
async def get_articles_tool(args: ParkModelArgs):
    """Tool that could Retrieve articles created by national parks 
    and other NPS entities. 
    (See "people" and "places" below for other specific article types.)"""
    
    client_url = nps_api_base_url + "/articles"

    return await src.api_utils.nps_get_park(args, client_url)

@mcp.tool()
async def get_all_activity_list_tool(args: GeneralModelArgs):
    """Tool that could Retrieve categories of activities 
    (astronomy, hiking, wildlife watching, etc.) and its ID
    possible in all national parks."""
    
    client_url = nps_api_base_url + "/activities"

    return await src.api_utils.nps_get_general(args, client_url)

@mcp.tool()
async def get_park_specific_activity_list_tool(args: ParkModelArgs):
    """Tool that could Retrieve national parks that are related to 
    particular categories of activity (astronomy, hiking, wildlife watching, etc.)
    in a specific park."""
    
    client_url = nps_api_base_url + "/activities/parks"

    return await src.api_utils.nps_get_park(args, client_url)

@mcp.tool()
async def get_all_amenities_list_tool(args: GeneralModelArgs):
    """Tool that could Retrieve the amenity types 
    such as accessible restrooms, fire pit, picnic area, etc. 
    available in all national parks."""
    
    client_url = nps_api_base_url + "/amenities"

    return await src.api_utils.nps_get_general(args, client_url)

@mcp.tool()
async def get_amenities_parkplaces_tool(args: ParkModelArgs):
    """Tool that could Retrieve "places" within national parks 
    that have different amenities"""
    
    client_url = nps_api_base_url + "/amenities/parksplaces"

    return await src.api_utils.nps_get_park(args, client_url)

@mcp.tool()
async def get_park_specific_visitorcenter_with_amenities_tool(args: ParkModelArgs):
    """Tool that could Retrieve visitor centers within a specific national parks 
    that have different amenities."""
    
    client_url = nps_api_base_url + "/amenities/parksvisitorcenters"

    return await src.api_utils.nps_get_park(args, client_url)

@mcp.tool()
async def get_campgrounds_tool(args: ParkModelArgs):
    """Tool that could Retrieve data about National Park Service 
    campgrounds including addresses, contacts, description, 
    hours of operation, etc."""
    
    client_url = nps_api_base_url + "/campgrounds"

    return await src.api_utils.nps_get_park(args, client_url)

@mcp.tool()
async def get_events_tool(args: ParkModelArgs):
    """Tool that retrieves events from parks including dates, 
    descriptions, and times created by national parks and other entities"""
    
    client_url = nps_api_base_url + "/events"
    return await src.api_utils.nps_get_park(args, client_url)

@mcp.tool()
async def get_feespasses_tool(args: ParkModelArgs):
    """Tool that retrieves information about fees and passes 
    created by national parks and other NPS entities"""
    
    client_url = nps_api_base_url + "/feespasses"
    return await src.api_utils.nps_get_park(args, client_url)

@mcp.tool()
async def get_lesson_plans_tool(args: ParkModelArgs):
    """Tool that retrieve lesson plans created by national 
    parks and other NPS entities."""
    
    client_url = nps_api_base_url + "/lessonplans"
    return await src.api_utils.nps_get_park(args, client_url)


if __name__ == "__main__":
    mcp.run(transport="stdio")