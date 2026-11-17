from contextlib import asynccontextmanager

from fastapi import FastAPI
from langchain.mcp import MCPAdapter

from app.agent.personal_chief import initialize_agent
from app.mcp.connections import MCP_GROUP
from app.tools.tavily import create_controlled_tavily_tool
from app.tools.tinyfish import create_controlled_tinifish


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with MCPAdapter(MCP_GROUP) as adapter:
        mcp_tools = await adapter.list_tools()
        tavily_tool = next(
            (tool for tool in mcp_tools if tool.name == "tavily_tavily_search"), None
        )
        tinyfish_tool = next(
            (tool for tool in mcp_tools if tool.name == "tinyFish_fetch_content"), None
        )
        if tavily_tool is None or tinyfish_tool is None:
            raise RuntimeError("Uma ou mais ferramentas MCP necessárias não estão disponíveis.")

        tools = [
            create_controlled_tavily_tool(tavily_tool, max_calls=5),
            create_controlled_tinifish(tinyfish_tool),
        ]
        app.state.agent = await initialize_agent(tools)
        yield
        del app.state.agent
