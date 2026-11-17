from langchain.tools import tool

def create_controlled_tinifish(mcp_tool):

    @tool('tinyFish_fetch_content')
    async def controlled_tinifish_fetch_content(purpose: str, urls: list[str]):
        """Extract web content from web page"""

        if not purpose.strip():
            raise ValueError("A pesquisa não pode estar vazia.")

        arguments = {
            "purpose": purpose,
            "format": "markdown",
            "urls": urls
        }

        return await mcp_tool.ainvoke(arguments)

    return controlled_tinifish_fetch_content
        