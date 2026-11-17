from fastmcp.client import Client
from fastmcp import ClientGroup

MCP_GROUP = ClientGroup({
    "tinyFish": Client("https://agent.tinyfish.ai/mcp", auth="oauth"),
    "tavily": Client("https://mcp.tavily.com/mcp/?tavilyApiKey=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")
})