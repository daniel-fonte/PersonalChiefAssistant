import asyncio

from dotenv import load_dotenv

load_dotenv()

from langchain.mcp import MCPAdapter
from langchain_core.messages import HumanMessage

from agents.personal_chief_agent import initialize_agent

from langchain.messages import AIMessageChunk, AIMessage, AnyMessage, ToolMessage
from mcp_clients.connections import MCP_GROUP
from tools.tavily_tools import create_controlled_tavily_tool
from tools.tinyFish_tools import create_controlled_tinifish

async def main():
    async with MCPAdapter(MCP_GROUP) as adapter:
        mcp_tools = await adapter.list_tools()

        for tool in mcp_tools:
            print("=" * 60)
            print("NAME:", tool.name)
            print("DESCRIPTION:", tool.description)

        originalSearchTavilyTool = next(
            tool for tool in mcp_tools if tool.name == "tavily_tavily_search"
        )

        originalTinifishFetchContent = next(
            tool for tool in mcp_tools if tool.name == "tinyFish_fetch_content"
        )

        tavily_search_controlled = create_controlled_tavily_tool(originalSearchTavilyTool, 5)
        tinifish_fetch_content_controlled = create_controlled_tinifish(originalTinifishFetchContent)

        # mcp_tools = [
        #     tavily_search_controlled
        #     if tool.name == "tavily_tavily_search"
        #     else tinifish_fetch_content_controlled
        #     if tool.name == "tinyFish_fetch_content"
        #     else tool
        #     for tool in mcp_tools
        # ]

        mcp_tools = [
            tavily_search_controlled,
            tinifish_fetch_content_controlled
        ]
        
        agent = await initialize_agent(mcp_tools)

        thread_config = { "configurable": {"thread_id": "1"} }

        question = HumanMessage(
            content="""
                Tenho interesse em preparar uma lasanha à bolonhesa, mas quero pesquisar antes de começar.

                Faça o seguinte:

                1. Use o Tavily para pesquisar uma receita de lasanha à bolonhesa na internet.
                2. Use o TinyFish para extrair o contéudo das receitas encontradas e liste os ingredientes, modo de preparo
                3. Pesquise a tabela nutricional de cada receita
            """
        )
        
        full_message = None

        async for chunk in agent.astream(
            {"messages": question},
            stream_mode=["messages", "updates"],
            version="v2",
            config=thread_config
        ):
            if chunk["type"] == "messages":
                token, metadata = chunk["data"]
                if isinstance(token, AIMessageChunk):
                    print(token.content, end="", flush=True)
                    full_message = token if full_message is None else full_message + token  
                    if token.chunk_position == "last":
                        if full_message.tool_calls:
                            print(f"Tool calls: {full_message.tool_calls}")
                        full_message = None
            elif chunk["type"] == "updates":
                for source, update in chunk["data"].items():
                    if source == "tools":
                        if isinstance(update["messages"][-1], ToolMessage):
                            print(f"Tool response: {update["messages"][-1].content_blocks}")

if __name__ == "__main__":
    asyncio.run(main())