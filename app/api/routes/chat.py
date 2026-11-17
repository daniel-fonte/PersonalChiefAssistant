from typing import Any

from fastapi import APIRouter, HTTPException, Request
from langchain_core.messages import HumanMessage

from app.api.schemas.chat import ChatRequest, ChatResponse
from app.tools.tavily import SearchState, tavily_state

router = APIRouter()


def _message_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    return str(content)


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, request: Request) -> ChatResponse:
    """Send a message to the agent and return its final answer."""
    state = SearchState()
    token = tavily_state.set(state)
    try:
        result = await request.app.state.agent.ainvoke(
            {"messages": [HumanMessage(content=payload.message)]},
            config={"configurable": {"thread_id": payload.thread_id}},
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Falha ao processar a mensagem.") from exc
    finally:
        tavily_state.reset(token)

    messages = result.get("messages", [])
    answer = next(
        (
            _message_text(message.content)
            for message in reversed(messages)
            if getattr(message, "type", None) == "ai"
        ),
        "",
    )
    return ChatResponse(response=answer, thread_id=payload.thread_id)
