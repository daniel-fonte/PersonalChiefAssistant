from langchain.tools import tool
from tavily import TavilyClient
from typing import Dict, Any
from services.tavily_service import TavilyService

tavilyService = TavilyService()

@tool()
def web_search(query: str) -> Dict[str, Any]:
    """Search web information"""

    return tavilyService.search(query)

