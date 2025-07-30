import os
import json
import asyncio
from dotenv import load_dotenv
import requests
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
from typing import Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
import uvicorn

load_dotenv(override=True)

# Initialize FastAPI app
app = FastAPI(title="NPS MCP Server")

# Initialize MCP server (for tool registration)
mcp = FastMCP("nps-info-server")
nps_api_base_url = "https://developer.nps.gov/api/v1"

class ParkModelArgs(BaseModel):
    park_code: Optional[str] = Field(description="Park code from NPS website")
    state_code: Optional[str] = Field(description="US state where the park is addressed")
    search_term: Optional[str] = Field(description="Term to search in the API output")

# LAZY LOADING: Define tools as regular functions that only check API key when called
def get_park_data(args: ParkModelArgs):
    """API request to NPS website to get retrieve data about national parks (addresses, contacts, description, hours of operation, etc.)"""
    
    # LAZY LOADING: Only check for API key when the tool is actually called
    api_key = os.getenv("NPS_API_KEY")
    if not api_key:
        return {
            "error": "NPS_API_KEY environment variable is required. Get your free API key from https://www.nps.gov/subjects/developer/"
        }
    
    params = {
        "parkCode": args.park_code,
        "stateCode": args.state_code,
        "q": args.search_term,
        "api_key": api_key
    }
    params = {k: v for k, v in params.items() if v is not None}
    
    headers = {"accept": "application/json"}
    client_url = nps_api_base_url + "/parks"
    
    try:
        response = requests.get(client_url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        return {"error": str(err)}

def get_passport_stamp_locations_data(args: ParkModelArgs):
    """API request to NPS website to get retrieve locations (see "campgrounds", "places", and "visitorcenters") that have national park passport stamps."""
    
    # LAZY LOADING: Only check for API key when the tool is actually called
    api_key = os.getenv("NPS_API_KEY")
    if not api_key:
        return {
            "error": "NPS_API_KEY environment variable is required. Get your free API key from https://www.nps.gov/subjects/developer/"
        }
    
    params = {
        "parkCode": args.park_code,
        "stateCode": args.state_code,
        "q": args.search_term,
        "api_key": api_key
    }
    params = {k: v for k, v in params.items() if v is not None}
    
    headers = {"accept": "application/json"}
    client_url = nps_api_base_url + "/passportstamplocations"
    
    try:
        response = requests.get(client_url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        return {"error": str(err)}

# Register tools with MCP (optional - for future MCP protocol compliance)
@mcp.tool()
def get_park(args: ParkModelArgs):
    """API request to NPS website to get retrieve data about national parks"""
    return get_park_data(args)

@mcp.tool()
def get_passport_stamp_locations(args: ParkModelArgs):
    """API request to NPS website to get passport stamp locations"""
    return get_passport_stamp_locations_data(args)

# LAZY LOADING: Define tools registry WITHOUT requiring API key validation
# This allows Smithery to scan tools without needing authentication
TOOLS_REGISTRY = {
    "get_park": {
        "name": "get_park",
        "description": "Get detailed information about national parks including addresses, contacts, description, hours of operation, entrance fees, and more. Works with park codes (e.g., 'yose' for Yosemite), state codes, or search terms.",
        "function": get_park_data,
        "input_schema": {
            "type": "object",
            "properties": {
                "park_code": {
                    "type": "string",
                    "description": "NPS park code (e.g., 'yose' for Yosemite, 'grca' for Grand Canyon)"
                },
                "state_code": {
                    "type": "string", 
                    "description": "US state code (e.g., 'CA', 'AZ', 'UT')"
                },
                "search_term": {
                    "type": "string",
                    "description": "Search term to find parks by name or keywords"
                }
            },
            "required": []
        }
    },
    "get_passport_stamp_locations": {
        "name": "get_passport_stamp_locations", 
        "description": "Find locations within national parks that have passport stamp stations. Passport stamps are collectible stamps available at visitor centers, campgrounds, and other park locations.",
        "function": get_passport_stamp_locations_data,
        "input_schema": {
            "type": "object",
            "properties": {
                "park_code": {
                    "type": "string",
                    "description": "NPS park code (e.g., 'yose' for Yosemite, 'grca' for Grand Canyon)"
                },
                "state_code": {
                    "type": "string",
                    "description": "US state code (e.g., 'CA', 'AZ', 'UT')"
                },
                "search_term": {
                    "type": "string",
                    "description": "Search term to filter stamp locations"
                }
            },
            "required": []
        }
    }
}

# LAZY LOADING: Smithery-required endpoints that work WITHOUT API key
@app.get("/mcp")
async def mcp_get():
    """Handle GET requests to /mcp - return server info and available tools
    
    IMPORTANT: This endpoint MUST work without requiring API keys or authentication
    for Smithery to be able to scan tools during deployment.
    """
    tools = []
    
    # Return tool definitions without validating API keys
    for tool_name, tool_info in TOOLS_REGISTRY.items():
        tools.append({
            "name": tool_info["name"],
            "description": tool_info["description"],
            "inputSchema": tool_info["input_schema"]
        })
    
    return {
        "server": "nps-info-server",
        "version": "1.0.0",
        "tools": tools,
        "status": "ready",
        "message": "Tools are available. API key validation happens during tool execution."
    }

@app.post("/mcp")
async def mcp_post(request: Request):
    """Handle POST requests to /mcp - execute MCP tools
    
    This is where authentication/API key validation happens (lazy loading).
    """
    try:
        body = await request.json()
        
        # Extract tool name and arguments
        tool_name = body.get("tool")
        args = body.get("arguments", {})
        
        if not tool_name:
            raise HTTPException(status_code=400, detail="Missing 'tool' parameter")
        
        # Check if tool exists
        if tool_name not in TOOLS_REGISTRY:
            available_tools = list(TOOLS_REGISTRY.keys())
            raise HTTPException(
                status_code=404, 
                detail=f"Tool '{tool_name}' not found. Available tools: {available_tools}"
            )
        
        # Execute the tool (this is where API key validation happens)
        tool_info = TOOLS_REGISTRY[tool_name]
        args_model = ParkModelArgs(**args)
        result = tool_info["function"](args_model)
        
        return {
            "tool": tool_name,
            "result": result,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/mcp")
async def mcp_delete():
    """Handle DELETE requests to /mcp - cleanup/reset"""
    return {
        "status": "cleaned",
        "message": "Server state reset"
    }

# Health check endpoint - MUST work without API key
@app.get("/health")
async def health_check():
    """Health check endpoint - works without requiring API key"""
    api_key = os.getenv("NPS_API_KEY")
    return {
        "status": "healthy",
        "server": "nps-info-server",
        "api_key_configured": bool(api_key),
        "tools_count": len(TOOLS_REGISTRY),
        "message": "Server is running. Tools will validate API key when called."
    }

# Root endpoint - MUST work without API key
@app.get("/")
async def root():
    """Root endpoint - works without requiring API key"""
    return {
        "message": "NPS MCP Server - National Park Service Information",
        "description": "Get information about national parks and passport stamp locations",
        "endpoints": {
            "mcp": "/mcp (GET, POST, DELETE)",
            "health": "/health",
            "docs": "/docs"
        },
        "tools": list(TOOLS_REGISTRY.keys()),
        "setup_instructions": "Set NPS_API_KEY environment variable. Get your free API key from https://www.nps.gov/subjects/developer/"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    
    # DON'T exit if API key is missing - let it run for tool scanning
    api_key = os.getenv("NPS_API_KEY")
    if not api_key:
        print("Info: NPS_API_KEY not set. Tools will return error messages when called without API key.")
        print("Get your free API key from: https://www.nps.gov/subjects/developer/")
    
    print(f"Starting server on port {port}")
    print(f"MCP endpoint available at: http://localhost:{port}/mcp")
    print(f"Available tools: {list(TOOLS_REGISTRY.keys())}")
    print("Server implements lazy loading - API key validation happens during tool execution.")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level="info"
    )