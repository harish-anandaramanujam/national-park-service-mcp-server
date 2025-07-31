# server.py
from mcp.server.fastmcp import FastMCP
from app import reverse_text


mcp = FastMCP("simple-mcp")

@mcp.tool()
async def reverse_text_tool(text: str) -> str:
    """
    MCP server to reverse a text
    """
    return reverse_text(text)

if __name__ == "__main__":
    mcp.run(transport="stdio")