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


# Extract API key from Smithery's base64-encoded config parameter
class SmitheryConfigMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        global current_api_key
        
        if scope.get('type') == 'http' and scope.get('path') in ['/mcp', '/mcp/']:
            query_string = scope.get('query_string', b'').decode('utf-8')
            print(f"Processing request with query: {query_string}")
            if query_string:
                params = parse_qs(query_string)
                if 'config' in params:
                    try:
                        # URL decode then base64 decode config from Smithery
                        config_b64 = unquote(params['config'][0])
                        print(f"Config parameter (URL decoded): {config_b64}")
                        config_json = base64.b64decode(config_b64).decode('utf-8')
                        config = json.loads(config_json)
                        print(f"Parsed config: {config}")
                        
                        # Extract API key matching smithery.yaml schema
                        if 'apiKey' in config:
                            current_api_key = config['apiKey']
                            print(f"API key configured: {current_api_key[:10]}...")
                    except (json.JSONDecodeError, Exception, IndexError, KeyError) as e:
                        print(f"Error parsing config: {e}")
                        current_api_key = None
        
        await self.app(scope, receive, send)

# Handle /mcp path routing for MCP protocol
class MCPPathRedirect:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # Redirect /mcp to /mcp/ for proper routing
        if scope.get('type') == 'http' and scope.get('path') == '/mcp':
            scope['path'] = '/mcp/'
            scope['raw_path'] = b'/mcp/'
        await self.app(scope, receive, send)

if __name__ == "__main__":
    # Setup Starlette app with CORS for cross-origin requests
    app = mcp.streamable_http_app()
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["mcp-session-id"],
        max_age=86400,
    )

    # Apply custom middleware stack
    app = SmitheryConfigMiddleware(app)
    app = MCPPathRedirect(app)

    # Use Smithery-required PORT environment variable
    port = int(os.environ.get("PORT", 8080))

    print("Text Utils MCP Server starting...")
    print(f"Listening on port {port}")
    print("Example: count_character('strawberry', 'r') -> counts r's!")

    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info") 