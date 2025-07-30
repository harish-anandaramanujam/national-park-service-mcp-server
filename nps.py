import os
from dotenv import load_dotenv
import requests
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
from typing import Optional
from starlette.middleware.cors import CORSMiddleware
import uvicorn

load_dotenv(override=True)

mcp = FastMCP("nps-info-server")

nps_api_base_url = "https://developer.nps.gov/api/v1"


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
def get_passport_stamp_locations(args: ParkModelArgs):
    """API request to NPS website to get retrieve locations (see "campgrounds", "places", and "visitorcenters") that have national park passport stamps."""
    params = {
        "parkCode": args.park_code,
        "stateCode": args.state_code,
        "q": args.search_term,
        "api_key": os.getenv("NPS_API_KEY")
    }
    headers = {
        "accept": "application/json"
    }
    client_url = nps_api_base_url + "/passportstamplocations"
    
    try:
        response = requests.get(client_url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        return {"error": str(err)}


class MCPPathRedirect:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get('type') == 'http' and scope.get('path') == '/mcp':
            scope['path'] = '/mcp/'
            scope['raw_path'] = b'/mcp/'
        await self.app(scope, receive, send)

if __name__ == "__main__":
    # Get the Starlette app and add CORS middleware
    app = mcp.streamable_http_app()
    
    # Add CORS middleware with proper header exposure for MCP session management
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure this more restrictively in production
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["mcp-session-id"],  # Allow client to read session ID
        max_age=86400,
    )

    # Apply the MCPPathRedirect middleware to prevent auto-redirect
    app = MCPPathRedirect(app)

    # Use PORT environment variable (required by Smithery)
    port = int(os.environ.get("PORT", 8080))

    # Run the MCP server with HTTP transport using uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",  # Listen on all interfaces for containerized deployment
        port=port,
        log_level="info"
    )