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

# Initialize MCP server
mcp = FastMCP("nps-info-server")
nps_api_base_url = "https://developer.nps.gov/api/v1"

class ParkModelArgs(BaseModel):
    park_code: Optional[str] = Field(description="Park code from NPS website")
    state_code: Optional[str] = Field(description="US state where the park is addressed")
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
    params = {k: v for k, v in params.items() if v is not None}
    
    headers = {"accept": "application/json"}
    client_url = nps_api_base_url + "/parks"
    
    try:
        response = requests.get(client_url, params=params, headers=headers, timeout=30)
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
    params = {k: v for k, v in params.items() if v is not None}
    
    headers = {"accept": "application/json"}
    client_url = nps_api_base_url + "/passportstamplocations"
    
    try:
        response = requests.get(client_url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        return {"error": str(err)}

# Smithery-required endpoints
@app.get("/mcp")
async def mcp_get():
    """Handle GET requests to /mcp - return server info and available tools"""
    tools = []
    
    # Get tools from MCP server
    for tool_name, tool_info in mcp._tools.items():
        tools.append({
            "name": tool_name,
            "description": tool_info.get("description", ""),
            "inputSchema": tool_info.get("inputSchema", {})
        })
    
    return {
        "server": "nps-info-server",
        "version": "1.0.0",
        "tools": tools,
        "status": "ready"
    }

@app.post("/mcp")
async def mcp_post(request: Request):
    """Handle POST requests to /mcp - execute MCP tools"""
    try:
        body = await request.json()
        
        # Extract tool name and arguments
        tool_name = body.get("tool")
        args = body.get("arguments", {})
        
        if not tool_name:
            raise HTTPException(status_code=400, detail="Missing 'tool' parameter")
        
        # Execute the tool
        if tool_name == "get_park":
            result = get_park(ParkModelArgs(**args))
        elif tool_name == "get_passport_stamp_locations":
            result = get_passport_stamp_locations(ParkModelArgs(**args))
        else:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
        
        return {
            "tool": tool_name,
            "result": result,
            "status": "success"
        }

        # return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/mcp")
async def mcp_delete():
    """Handle DELETE requests to /mcp - cleanup/reset"""
    return {
        "status": "cleaned",
        "message": "Server state reset"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    api_key = os.getenv("NPS_API_KEY")
    return {
        "status": "healthy",
        "server": "nps-info-server",
        "api_key_configured": bool(api_key),
        "tools_count": len(mcp._tools)
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "NPS MCP Server",
        "endpoints": {
            "mcp": "/mcp (GET, POST, DELETE)",
            "health": "/health",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    
    # Check for required environment variables
    if not os.getenv("NPS_API_KEY"):
        print("Warning: NPS_API_KEY environment variable not set!")
    
    print(f"Starting server on port {port}")
    print(f"MCP endpoint available at: http://localhost:{port}/mcp")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level="info"
    )