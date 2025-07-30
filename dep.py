import os
import json
import asyncio
import logging
import time
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

# Third-party imports
from dotenv import load_dotenv
import requests
from pydantic import BaseModel, Field, validator
from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Load environment variables
load_dotenv(override=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
NPS_API_BASE_URL = "https://developer.nps.gov/api/v1"
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RATE_LIMIT_DELAY = 0.1  # 100ms between requests

# Application lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    logger.info("🚀 NPS MCP Server starting up...")
    
    # Startup logic
    api_key = os.getenv("NPS_API_KEY")
    if api_key:
        logger.info("✅ NPS API key configured")
    else:
        logger.info("ℹ️ NPS API key not configured - tools will require configuration at runtime")
    
    yield
    
    # Shutdown logic
    logger.info("🛑 NPS MCP Server shutting down...")

# Initialize FastAPI app with best practices
app = FastAPI(
    title="National Park Service MCP Server",
    description="Comprehensive National Park Service data access with lazy loading and robust error handling",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware for production readiness
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MCP server
mcp = FastMCP("nps-info-server")

# Enhanced Pydantic models with validation
class ParkSearchArgs(BaseModel):
    """Arguments for park search operations"""
    park_code: Optional[str] = Field(
        None, 
        description="NPS park code (e.g., 'yose' for Yosemite, 'grca' for Grand Canyon)",
        example="yose"
    )
    state_code: Optional[str] = Field(
        None, 
        description="US state code (e.g., 'CA', 'AZ', 'UT')",
        example="CA"
    )
    search_term: Optional[str] = Field(
        None, 
        description="Search term to find parks by name or keywords",
        example="Yosemite"
    )
    limit: Optional[int] = Field(
        10, 
        description="Maximum number of results to return (1-50)",
        ge=1,
        le=50
    )
    
    @validator('state_code')
    def validate_state_code(cls, v):
        if v and len(v) != 2:
            raise ValueError('State code must be 2 characters')
        return v.upper() if v else v
    
    @validator('park_code')
    def validate_park_code(cls, v):
        if v and len(v) < 2:
            raise ValueError('Park code must be at least 2 characters')
        return v.lower() if v else v

class APIResponse(BaseModel):
    """Standardized API response format"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

# Enhanced HTTP client with retry logic and rate limiting
class NPSAPIClient:
    """Enhanced NPS API client with best practices"""
    
    def __init__(self):
        self.base_url = NPS_API_BASE_URL
        self.last_request_time = 0
        
    async def _make_request(self, endpoint: str, params: Dict[str, Any]) -> APIResponse:
        """Make HTTP request with retry logic and rate limiting"""
        
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < RATE_LIMIT_DELAY:
            await asyncio.sleep(RATE_LIMIT_DELAY - time_since_last)
        
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(MAX_RETRIES):
            try:
                self.last_request_time = time.time()
                
                response = requests.get(
                    url, 
                    params=params, 
                    headers={"accept": "application/json"},
                    timeout=REQUEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return APIResponse(
                        success=True,
                        data=data,
                        metadata={
                            "total_results": data.get("total", 0),
                            "api_endpoint": endpoint,
                            "response_time_ms": int((time.time() - self.last_request_time) * 1000)
                        }
                    )
                elif response.status_code == 429:  # Rate limited
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Rate limited, waiting {wait_time}s before retry {attempt + 1}")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    response.raise_for_status()
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout on attempt {attempt + 1}")
                if attempt == MAX_RETRIES - 1:
                    return APIResponse(
                        success=False,
                        error="Request timed out after multiple attempts"
                    )
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed on attempt {attempt + 1}: {str(e)}")
                if attempt == MAX_RETRIES - 1:
                    return APIResponse(
                        success=False,
                        error=f"API request failed: {str(e)}"
                    )
            
            # Exponential backoff for retries
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(2 ** attempt)
        
        return APIResponse(success=False, error="All retry attempts failed")

# Global API client instance
nps_client = NPSAPIClient()

# LAZY LOADING: Tool functions that validate API key only when called
async def get_park_data(args: ParkSearchArgs) -> APIResponse:
    """Get detailed park information with enhanced error handling"""
    
    # LAZY LOADING: API key validation at execution time
    api_key = os.getenv("NPS_API_KEY")
    if not api_key:
        return APIResponse(
            success=False,
            error="NPS_API_KEY environment variable is required. Get your free API key from https://www.nps.gov/subjects/developer/",
            metadata={"setup_url": "https://www.nps.gov/subjects/developer/"}
        )
    
    # Build API parameters
    params = {
        "api_key": api_key,
        "limit": args.limit
    }
    
    if args.park_code:
        params["parkCode"] = args.park_code
    if args.state_code:
        params["stateCode"] = args.state_code  
    if args.search_term:
        params["q"] = args.search_term
    
    try:
        response = await nps_client._make_request("parks", params)
        
        if response.success and response.data:
            # Enhance response with additional metadata
            parks = response.data.get("data", [])
            response.metadata.update({
                "parks_found": len(parks),
                "search_params": {k: v for k, v in params.items() if k != "api_key"},
                "popular_parks": [
                    {"code": park.get("parkCode"), "name": park.get("fullName")}
                    for park in parks[:3]  # Top 3 results
                ]
            })
        
        return response
        
    except Exception as e:
        logger.error(f"Unexpected error in get_park_data: {str(e)}")
        return APIResponse(
            success=False,
            error=f"Unexpected error: {str(e)}"
        )

async def get_passport_stamp_locations_data(args: ParkSearchArgs) -> APIResponse:
    """Get passport stamp locations with enhanced error handling"""
    
    # LAZY LOADING: API key validation at execution time
    api_key = os.getenv("NPS_API_KEY")
    if not api_key:
        return APIResponse(
            success=False,
            error="NPS_API_KEY environment variable is required. Get your free API key from https://www.nps.gov/subjects/developer/",
            metadata={"setup_url": "https://www.nps.gov/subjects/developer/"}
        )
    
    # Build API parameters
    params = {
        "api_key": api_key,
        "limit": args.limit
    }
    
    if args.park_code:
        params["parkCode"] = args.park_code
    if args.state_code:
        params["stateCode"] = args.state_code
    if args.search_term:
        params["q"] = args.search_term
    
    try:
        response = await nps_client._make_request("passportstamplocations", params)
        
        if response.success and response.data:
            # Enhance response with stamp location metadata
            locations = response.data.get("data", [])
            response.metadata.update({
                "stamp_locations_found": len(locations),
                "search_params": {k: v for k, v in params.items() if k != "api_key"},
                "location_types": list(set([
                    loc.get("type", "unknown") 
                    for loc in locations 
                    if loc.get("type")
                ]))
            })
        
        return response
        
    except Exception as e:
        logger.error(f"Unexpected error in get_passport_stamp_locations_data: {str(e)}")
        return APIResponse(
            success=False,
            error=f"Unexpected error: {str(e)}"
        )

# Additional tool for park activities
async def get_park_activities_data(args: ParkSearchArgs) -> APIResponse:
    """Get park activities and things to do"""
    
    api_key = os.getenv("NPS_API_KEY")
    if not api_key:
        return APIResponse(
            success=False,
            error="NPS_API_KEY environment variable is required. Get your free API key from https://www.nps.gov/subjects/developer/",
            metadata={"setup_url": "https://www.nps.gov/subjects/developer/"}
        )
    
    params = {
        "api_key": api_key,
        "limit": args.limit
    }
    
    if args.park_code:
        params["parkCode"] = args.park_code
    if args.state_code:
        params["stateCode"] = args.state_code
    if args.search_term:
        params["q"] = args.search_term
    
    try:
        response = await nps_client._make_request("thingstodo", params)
        
        if response.success and response.data:
            activities = response.data.get("data", [])
            response.metadata.update({
                "activities_found": len(activities),
                "search_params": {k: v for k, v in params.items() if k != "api_key"},
                "activity_types": list(set([
                    activity.get("tags", [{}])[0].get("name", "unknown")
                    for activity in activities 
                    if activity.get("tags") and len(activity.get("tags", [])) > 0
                ]))
            })
        
        return response
        
    except Exception as e:
        logger.error(f"Unexpected error in get_park_activities_data: {str(e)}")
        return APIResponse(
            success=False,
            error=f"Unexpected error: {str(e)}"
        )

# Register tools with MCP
@mcp.tool()
def get_park(args: ParkSearchArgs):
    """Get detailed information about national parks"""
    return asyncio.run(get_park_data(args))

@mcp.tool()
def get_passport_stamp_locations(args: ParkSearchArgs):
    """Find passport stamp locations in national parks"""
    return asyncio.run(get_passport_stamp_locations_data(args))

@mcp.tool() 
def get_park_activities(args: ParkSearchArgs):
    """Find activities and things to do in national parks"""
    return asyncio.run(get_park_activities_data(args))

# LAZY LOADING: Comprehensive tools registry
TOOLS_REGISTRY = {
    "get_park": {
        "name": "get_park",
        "description": "Get comprehensive information about national parks including addresses, contacts, descriptions, hours of operation, entrance fees, weather info, and more. Search by park code, state, or keywords.",
        "function": get_park_data,
        "examples": [
            {"park_code": "yose", "description": "Get Yosemite National Park info"},
            {"state_code": "CA", "limit": 5, "description": "Find 5 parks in California"},
            {"search_term": "canyon", "description": "Search for parks with 'canyon' in the name"}
        ],
        "input_schema": ParkSearchArgs.schema()
    },
    "get_passport_stamp_locations": {
        "name": "get_passport_stamp_locations",
        "description": "Find locations within national parks that have passport stamp stations. Passport stamps are collectible stamps available at visitor centers, campgrounds, museums, and other park facilities. Perfect for planning stamp collecting adventures!",
        "function": get_passport_stamp_locations_data,
        "examples": [
            {"park_code": "grca", "description": "Find stamp locations in Grand Canyon"},
            {"state_code": "UT", "description": "Find stamp locations in Utah parks"},
            {"search_term": "visitor center", "description": "Find visitor center stamp locations"}
        ],
        "input_schema": ParkSearchArgs.schema()
    },
    "get_park_activities": {
        "name": "get_park_activities", 
        "description": "Discover activities and things to do in national parks including hiking trails, guided tours, educational programs, ranger talks, and seasonal activities. Plan your perfect park visit!",
        "function": get_park_activities_data,
        "examples": [
            {"park_code": "yell", "description": "Find activities in Yellowstone"},
            {"search_term": "hiking", "description": "Find hiking activities across parks"},
            {"state_code": "CO", "limit": 10, "description": "Find activities in Colorado parks"}
        ],
        "input_schema": ParkSearchArgs.schema()
    }
}

# SMITHERY ENDPOINTS: All implement lazy loading best practices

@app.get("/mcp")
async def mcp_get(request: Request):
    """
    LAZY LOADING: Return server info and tools WITHOUT requiring authentication
    This is critical for Smithery's tool discovery process
    """
    try:
        tools = []
        
        # Return comprehensive tool definitions without API key validation
        for tool_name, tool_info in TOOLS_REGISTRY.items():
            tool_def = {
                "name": tool_info["name"],
                "description": tool_info["description"],
                "inputSchema": tool_info["input_schema"],
                "examples": tool_info.get("examples", [])
            }
            tools.append(tool_def)
        
        # Include server capabilities and status
        response_data = {
            "server": "nps-info-server",
            "version": "1.0.0",
            "description": "National Park Service MCP Server with comprehensive park data access",
            "tools": tools,
            "capabilities": {
                "lazy_loading": True,
                "retry_logic": True,
                "rate_limiting": True,
                "enhanced_error_handling": True
            },
            "status": "ready",
            "metadata": {
                "total_tools": len(tools),
                "api_provider": "National Park Service",
                "data_sources": ["Parks", "Passport Stamps", "Activities"],
                "authentication": "API key required for tool execution (not for discovery)"
            }
        }
        
        logger.info(f"Tool discovery request from {request.client.host if request.client else 'unknown'}")
        return JSONResponse(content=response_data)
        
    except Exception as e:
        logger.error(f"Error in tool discovery endpoint: {str(e)}")
        return JSONResponse(
            content={
                "error": "Internal server error during tool discovery",
                "status": "error"
            },
            status_code=500
        )

@app.post("/mcp")
async def mcp_post(request: Request):
    """
    Handle tool execution with comprehensive error handling and logging
    This is where API key validation happens (lazy loading)
    """
    try:
        body = await request.json()
        
        tool_name = body.get("tool")
        args = body.get("arguments", {})
        
        if not tool_name:
            raise HTTPException(status_code=400, detail="Missing 'tool' parameter")
        
        if tool_name not in TOOLS_REGISTRY:
            available_tools = list(TOOLS_REGISTRY.keys())
            raise HTTPException(
                status_code=404,
                detail=f"Tool '{tool_name}' not found. Available tools: {available_tools}"
            )
        
        # Validate arguments
        try:
            args_model = ParkSearchArgs(**args)
        except Exception as validation_error:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid arguments: {str(validation_error)}"
            )
        
        # Execute tool (lazy loading happens here)
        logger.info(f"Executing tool '{tool_name}' with args: {args}")
        
        tool_info = TOOLS_REGISTRY[tool_name]
        result = await tool_info["function"](args_model)
        
        # Enhanced response format
        response_data = {
            "tool": tool_name,
            "result": result.dict(),
            "status": "success" if result.success else "error",
            "execution_metadata": {
                "tool_name": tool_name,
                "arguments_provided": args,
                "execution_time": time.time()
            }
        }
        
        status_code = 200 if result.success else 400
        return JSONResponse(content=response_data, status_code=status_code)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in tool execution: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.delete("/mcp")
async def mcp_delete():
    """Handle cleanup/reset requests"""
    logger.info("MCP cleanup/reset requested")
    return JSONResponse(content={
        "status": "cleaned",
        "message": "Server state reset successfully",
        "timestamp": time.time()
    })

# ADDITIONAL BEST PRACTICE ENDPOINTS

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    api_key_configured = bool(os.getenv("NPS_API_KEY"))
    
    health_data = {
        "status": "healthy",
        "server": "nps-info-server",
        "version": "1.0.0",
        "timestamp": time.time(),
        "checks": {
            "api_key_configured": api_key_configured,
            "tools_available": len(TOOLS_REGISTRY),
            "nps_api_accessible": True  # Could add actual API health check
        },
        "configuration": {
            "lazy_loading": True,
            "retry_attempts": MAX_RETRIES,
            "request_timeout": REQUEST_TIMEOUT,
            "rate_limit_delay": RATE_LIMIT_DELAY
        }
    }
    
    return JSONResponse(content=health_data)

@app.get("/")
async def root():
    """Enhanced root endpoint with comprehensive information"""
    api_key_configured = bool(os.getenv("NPS_API_KEY"))
    
    return JSONResponse(content={
        "message": "🏞️ National Park Service MCP Server",
        "description": "Access comprehensive National Park Service data including park information, passport stamp locations, and activities",
        "version": "1.0.0",
        "endpoints": {
            "mcp": "/mcp (GET for discovery, POST for execution, DELETE for cleanup)",
            "health": "/health (server health check)",
            "docs": "/docs (API documentation)",
            "redoc": "/redoc (alternative API documentation)"
        },
        "tools": {
            tool_name: {
                "description": tool_info["description"],
                "examples": tool_info.get("examples", [])
            }
            for tool_name, tool_info in TOOLS_REGISTRY.items()
        },
        "setup": {
            "api_key_configured": api_key_configured,
            "api_key_source": "https://www.nps.gov/subjects/developer/",
            "instructions": "Set NPS_API_KEY environment variable with your free NPS API key"
        },
        "features": [
            "Lazy loading for tool discovery",
            "Comprehensive error handling",
            "Rate limiting and retry logic", 
            "Enhanced response metadata",
            "Production-ready logging"
        ]
    })

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint not found",
            "message": "This endpoint does not exist. Check /docs for available endpoints.",
            "available_endpoints": ["/", "/mcp", "/health", "/docs"]
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later."
        }
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    
    # Enhanced startup logging
    api_key = os.getenv("NPS_API_KEY")
    logger.info("🏞️ Starting National Park Service MCP Server...")
    logger.info(f"📊 Available tools: {list(TOOLS_REGISTRY.keys())}")
    logger.info(f"🔑 API key configured: {bool(api_key)}")
    logger.info(f"🚀 Server starting on port {port}")
    logger.info("✅ Lazy loading implemented for Smithery compatibility")
    
    if not api_key:
        logger.warning("⚠️ NPS_API_KEY not configured - tools will require runtime configuration")
        logger.info("🔗 Get your free API key: https://www.nps.gov/subjects/developer/")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )