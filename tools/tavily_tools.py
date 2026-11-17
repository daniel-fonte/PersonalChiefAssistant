
from langchain.tools import tool
import json
import asyncio

from contextvars import ContextVar
from dataclasses import dataclass, field


@dataclass
class SearchState:
    count: int = 0
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)


tavily_state = ContextVar("tavily_state", default=None)


def create_controlled_tavily_tool(mcp_tool, max_calls=1):

    @tool("tavily_search")
    async def controlled_tavily_search(query: str) -> str:
        """Pesquisa na internet usando Tavily."""

        if not query.strip():
            raise ValueError("A pesquisa não pode estar vazia.")

        state = tavily_state.get()

        if state is None:
            raise RuntimeError(
                "Tavily executado fora de uma execução controlada."
            )

        async with state.lock:

            if state.count >= max_calls:
                return (
                    f"Limite de {max_calls} pesquisas Tavily "
                    "atingido nesta execução."
                )

            state.count += 1
            current_count = state.count

        print(f"Tavily calls: {current_count}/{max_calls}")

        arguments = {
            "query": query,
            "max_results": 3,
            "search_depth": "basic",
            "time_range": "year"
        }

        result = await mcp_tool.ainvoke(arguments)

        # Extrai o texto retornado pelo MCP
        text_content = result[0]["text"]

        data = json.loads(text_content)

        # Aceita tanto uma lista quanto um objeto com results
        items = data if isinstance(data, list) else data.get("results", [])

        results = [
            {
                "title": item.get("title"),
                "url": item.get("url")
            }
            for item in items
        ]

        return json.dumps(results, ensure_ascii=False)

    return controlled_tavily_search
