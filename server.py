# server.py
import os
from dotenv import load_dotenv
import requests
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
from typing import Optional
import src.api_utils
from src.models import ParkModelArgs, GeneralModelArgs
import uvicorn
from starlette.middleware.cors import CORSMiddleware
from src.middleware import SmitheryConfigMiddleware

mcp = FastMCP("nps-info-server")

nps_api_base_url = "https://developer.nps.gov/api/v1"

# Load environment variables
if not os.getenv("NPS_API_KEY"):
    load_dotenv()

try:
    NPS_API_KEY = os.getenv("NPS_API_KEY")
except: 
    pass

def get_request_config() -> dict:
    """Get full config from current request context."""
    try:
        import contextvars
        request = contextvars.copy_context().get('request')
        if hasattr(request, 'scope') and request.scope:
            return request.scope.get('smithery_config', {})
    except:
        pass
    return {}

def get_config_value(key: str, default=None):
    """Get a specific config value from current request."""
    config = get_request_config()
    return config.get(key, default)

def get_api_key() -> Optional[str]:
    """Get API key from either request config or environment."""
    return get_config_value('npsApiKey') or NPS_API_KEY

@mcp.tool()
async def get_park_tool(args: ParkModelArgs):
    """Tool that could retrieve data about national parks (addresses, contacts, description, 
    hours of operation, etc.)"""
    
    api_key = get_api_key()
    if not api_key:
        return {"error": "NPS API key not configured"}
    
    client_url = nps_api_base_url + "/parks"
    return await src.api_utils.nps_get_park(args, client_url, api_key)

@mcp.tool()
async def get_passport_stamp_locations_tool(args: ParkModelArgs):
    """Tool that could get retrieve locations (see "campgrounds",
    "places", and "visitorcenters") that have national park
    passport stamps."""
    
    api_key = get_api_key()
    if not api_key:
        return {"error": "NPS API key not configured"}
    
    client_url = nps_api_base_url + "/passportstamplocations"
    return await src.api_utils.nps_get_park(args, client_url, api_key)

@mcp.tool()
async def get_alerts_tool(args: ParkModelArgs):
    """Tool that could Retrieve alerts (danger, closure, caution, and information) 
    posted by parks."""
    
    api_key = get_api_key()
    if not api_key:
        return {"error": "NPS API key not configured"}
    
    client_url = nps_api_base_url + "/alerts"
    return await src.api_utils.nps_get_park(args, client_url, api_key)

@mcp.tool()
async def get_articles_tool(args: ParkModelArgs):
    """Tool that could Retrieve articles created by national parks 
    and other NPS entities."""
    
    api_key = get_api_key()
    if not api_key:
        return {"error": "NPS API key not configured"}
    
    client_url = nps_api_base_url + "/articles"
    return await src.api_utils.nps_get_park(args, client_url, api_key)

@mcp.tool()
async def get_all_activity_list_tool(args: GeneralModelArgs):
    """Tool that could Retrieve categories of activities 
    (astronomy, hiking, wildlife watching, etc.) and its ID
    possible in all national parks."""
    
    api_key = get_api_key()
    if not api_key:
        return {"error": "NPS API key not configured"}
    
    client_url = nps_api_base_url + "/activities"
    return await src.api_utils.nps_get_general(args, client_url, api_key)

@mcp.tool()
async def get_park_specific_activity_list_tool(args: ParkModelArgs):
    """Tool that could Retrieve national parks that are related to 
    particular categories of activity (astronomy, hiking, wildlife watching, etc.)
    in a specific park."""
    
    api_key = get_api_key()
    if not api_key:
        return {"error": "NPS API key not configured"}
    
    client_url = nps_api_base_url + "/activities/parks"
    return await src.api_utils.nps_get_park(args, client_url, api_key)

# Continue this pattern for all other tools...
# I'll show a few more examples:

@mcp.tool()
async def get_campgrounds_tool(args: ParkModelArgs):
    """Tool that could Retrieve data about National Park Service 
    campgrounds including addresses, contacts, description, 
    hours of operation, etc."""
    
    api_key = get_api_key()
    if not api_key:
        return {"error": "NPS API key not configured"}
    
    client_url = nps_api_base_url + "/campgrounds"
    return await src.api_utils.nps_get_park(args, client_url, api_key)

@mcp.tool()
async def get_events_tool(args: ParkModelArgs):
    """Tool that retrieves events from parks including dates, 
    descriptions, and times created by national parks and other entities"""
    
    api_key = get_api_key()
    if not api_key:
        return {"error": "NPS API key not configured"}
    
    client_url = nps_api_base_url + "/events"
    return await src.api_utils.nps_get_park(args, client_url, api_key)

# ... (continue this pattern for ALL remaining tools)

def main():
    """Main entry point for Smithery deployment."""
    print("NPS MCP Server starting in HTTP mode for Smithery...")
    
    # Setup Starlette app with CORS
    app = mcp.streamable_http_app()
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["mcp-session-id", "mcp-protocol-version"],
        max_age=86400,
    )

    # Apply Smithery config middleware
    app = SmitheryConfigMiddleware(app)

    # Use PORT environment variable (required by Smithery)
    port = int(os.environ.get("PORT", 8081))
    print(f"Listening on port {port}")

    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

if __name__ == "__main__":
    main()