from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    """Input accepted by the chat endpoint."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    message: str = Field(strict=True, min_length=1, description="Mensagem enviada ao agente")
    thread_id: str = Field(strict=True, min_length=1, max_length=128)


class ChatResponse(BaseModel):
    """Agent reply returned by the chat endpoint."""

    response: str
    thread_id: str
