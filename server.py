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
from typing import Optional
from src.middleware import SmitheryConfigMiddleware

mcp = FastMCP("nps-info-server")

nps_api_base_url = "https://developer.nps.gov/api/v1"

if not os.getenv("NPS_API_KEY"):
    load_dotenv()
try:
    NPS_API_KEY = os.getenv("NPS_API_KEY")
except: 
    pass


# src/main.py (continued - only add if you need configuration)

def handle_config(config: dict):
    """Handle configuration from Smithery - for backwards compatibility with stdio mode."""
    global _server_token
    if server_token := config.get('npsApiKey'):
        _server_token = server_token
    
# Store server token only for stdio mode (backwards compatibility)
_server_token: Optional[str] = None

def get_request_config() -> dict:
    """Get full config from current request context."""
    try:
        # Access the current request context from FastMCP
        import contextvars
        
        # Try to get from request context if available
        request = contextvars.copy_context().get('request')
        if hasattr(request, 'scope') and request.scope:
            return request.scope.get('smithery_config', {})
    except:
        pass

def get_config_value(key: str, default=None):
    """Get a specific config value from current request."""
    config = get_request_config()
    return config.get(key, default)

# def validate_server_access(server_token: Optional[str]) -> bool:
#     """Validate server token - accepts any string including empty ones for demo."""
#     # Validate against your server's auth system
#     # For demo purposes, we accept any non-empty token
#     return server_token is not None and len(server_token.strip()) > 0 if server_token else True


@mcp.tool()
async def get_park_tool(args: ParkModelArgs):
    """Tool that could retrieve 
    data about national parks (addresses, contacts, description, 
    hours of operation, etc.)"""
    
    api_key = get_config_value('npsApiKey') or NPS_API_KEY
    
    if not api_key:
        return {"error": "NPS API key not configured"}
    
    client_url = nps_api_base_url + "/parks"

    return await src.api_utils.nps_get_park(args, client_url, api_key)

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

@mcp.tool()
async def get_map_metadata_tool(args: ParkModelArgs):
    """Tool that Retrieve geometry boundaries for park s
    pecified by a site code. ."""

    client_url = nps_api_base_url + "/mapdata/parkboundaries/"

    return await src.api_utils.nps_get_map_metadata(args, client_url)



@mcp.tool()
async def get_audios_tool(args: ParkModelArgs):
    """Tool that Retrieve metadata relating to 
    audio files created by national parks."""
    
    client_url = nps_api_base_url + "multimedia/audio"
    return await src.api_utils.nps_get_park(args, client_url)

@mcp.tool()
async def get_multimedia_galleries_tool(args: ParkModelArgs):
    """Tool that Retrieve galleries created by 
    national parks and other NPS entities."""
    
    client_url = nps_api_base_url + "/multimedia/galleries"
    return await src.api_utils.nps_get_park(args, client_url)

@mcp.tool()
async def get_multimedia_galleries_assets_tool(args: ParkModelArgs):
    """Tool that Retrieve gallery assets by unique asset id, 
    or gallery id, etc."""
    
    client_url = nps_api_base_url + "/multimedia/galleries/assets"
    return await src.api_utils.nps_get_park(args, client_url)

@mcp.tool()
async def get_videos_tool(args: ParkModelArgs):
    """Tool that Retrieve metadata relating to video files 
    created by national parks."""
    
    client_url = nps_api_base_url + "multimedia/videos"
    return await src.api_utils.nps_get_park(args, client_url)

@mcp.tool()
async def get_news_releases_tool(args: ParkModelArgs):
    """Tool that retrieves news releases about national parks, 
    including press releases and announcements."""
    
    client_url = nps_api_base_url + "/newsreleases"
    return await src.api_utils.nps_get_park(args, client_url)

@mcp.tool()
async def get_parkinglots_tool(args: ParkModelArgs):
    """Tool that Retrieve information related to parking lots 
    created by national parks and other NPS entities.."""
    
    client_url = nps_api_base_url + "/parkinglots"
    return await src.api_utils.nps_get_park(args, client_url)

@mcp.tool()
async def get_people_tool(args: ParkModelArgs):
    """Tool that retrieves information about people associated 
    with national parks, including park rangers and 
    scientists."""
    
    client_url = nps_api_base_url + "/people"
    return await src.api_utils.nps_get_park(args, client_url)

@mcp.tool()
async def get_places_tool(args: ParkModelArgs):
    """Tool that retrieves information about places within 
    national parks, including visitor centers, 
    museums, and other park facilities."""
    
    client_url = nps_api_base_url + "/places"
    return await src.api_utils.nps_get_park(args, client_url)

@mcp.tool()
async def get_roadevents_tool(args: ParkModelArgs):
    """Tool that Retrieve information relating to road events 
    by park and/or type of event (incident or workzone)."""
    
    client_url = nps_api_base_url + "/roadevents"
    return await src.api_utils.nps_get_park(args, client_url)

@mcp.tool()
async def get_thingstodo_tool(args: ParkModelArgs):
    """Tool that Retrieve suggested things to do recommended by 
    and for specific national parks."""
    
    client_url = nps_api_base_url + "/thingstodo"
    return await src.api_utils.nps_get_park(args, client_url)

@mcp.tool()
async def get_topics_tool(args: GeneralModelArgs):
    """Tool that Retrieve categories of topics 
    (American revolution, music, women's history, etc.) 
    relating to national parks.."""
    
    client_url = nps_api_base_url + "/topics"
    return await src.api_utils.nps_get_general(args, client_url)

@mcp.tool()
async def get_park_specific_topics_tool(args: ParkModelArgs):
    """Tool that Retrieve categories of topics 
    (American revolution, music, women's history, etc.) 
    relating to a specific national parks."""
    
    client_url = nps_api_base_url + "/topics/parks"
    return await src.api_utils.nps_get_park(args, client_url)

@mcp.tool()
async def get_tours_tool(args: ParkModelArgs):
    """Tool that Retrieve tours with stops at the special places, campgrounds, 
    and visitor centers found within national parks."""
    
    client_url = nps_api_base_url + "/tours"
    return await src.api_utils.nps_get_park(args, client_url)

@mcp.tool()
async def get_visitor_centers_tool(args: ParkModelArgs):
    """Tool that retrieves information about visitor centers 
    in national parks, including descriptions, 
    directions, and operating hours."""
    
    client_url = nps_api_base_url + "/visitorcenters"
    return await src.api_utils.nps_get_park(args, client_url)

@mcp.tool()
async def get_webcams_tool(args: ParkModelArgs):
    """Tool that retrieves information about webcams in 
    national parks, including webcam descriptions 
    and URLs."""
    
    client_url = nps_api_base_url + "/webcams"
    return await src.api_utils.nps_get_park(args, client_url)

# if __name__ == "__main__":
#     # mcp.run(transport="stdio")
#     mcp.run()

# src/main.py
def main():
    transport_mode = os.getenv("TRANSPORT", "stdio")

    transport_mode = "http"
    
    if transport_mode == "http":
        # HTTP mode with config extraction from URL parameters
        print("NPS MCP Server starting in HTTP mode...")
        
        # Setup Starlette app with CORS for cross-origin requests
        app = mcp.streamable_http_app()
        
        # IMPORTANT: add CORS middleware for browser based clients
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["*"],
            expose_headers=["mcp-session-id", "mcp-protocol-version"],
            max_age=86400,
        )

        # Apply custom middleware for config extraction (per-request API key handling)
        app = SmitheryConfigMiddleware(app)

        # Use Smithery-required PORT environment variable
        port = int(os.environ.get("PORT", 8081))
        print(f"Listening on port {port}")

        uvicorn.run(app, host="0.0.0.0", port=port, log_level="debug")
    
    else:
        # Optional: add stdio transport for backwards compatibility
        # You can publish this to uv for users to run locally
        print("NPS MCP Server starting in stdio mode...")
        
        server_token = os.getenv("NPS_API_KEY")
        # Set the server token for stdio mode (can be None)
        handle_config({"serverToken": server_token})
        
        # Run with stdio transport (default)
        mcp.run()

if __name__ == "__main__":
    main()