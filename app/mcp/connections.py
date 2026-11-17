from fastmcp.client import Client
from fastmcp import ClientGroup
from config import required_env

MCP_GROUP = ClientGroup({
    "tinyFish": Client("https://agent.tinyfish.ai/mcp", auth="oauth"),
    "tavily": Client(f"https://mcp.tavily.com/mcp/?tavilyApiKey={required_env('TAVILY_API_KEY')}")
})
