from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware, LLMToolSelectorMiddleware
from app.tools.tavily import SearchState, tavily_state
from app.prompts.personal_chief import SYSTEM_PROMPT, SUMMARY_PROMPT, TOOL_SELECTION_PROMPT

from langchain_groq import ChatGroq

# MODEL = "gpt-oss:20b"
MODEL = "openai/gpt-oss-120b"
# SUMARIZE_MODEL = "QyrouNnet/summarizer:400m"
SUMARIZE_MODEL = "openai/gpt-oss-20b"
# TOOL_SELECTION_MODEL = "qwen3:4b"
TOOL_SELECTION_MODEL = "qwen/qwen3.8-27b"

async def initialize_agent(tools):

    # TOOL_SELECTION_LLM = ChatOllama(
    #     model=TOOL_SELECTION_MODEL,
    #     temperature=0,          # Essencial para seleção determinística
    #     num_ctx=4096,           # Contexto enxuto economiza VRAM e acelera o prefill
    #     num_predict=1024,        # A resposta é apenas uma lista curta de nomes de tools
    #     reasoning=False,        # Desativa tokens de "pensamento" no Qwen 3 para resposta instantânea
    # )

    # SUMARIZE_LLM = ChatOllama(
    #     model=SUMARIZE_MODEL,
    #     temperature=0,          # Essencial para seleção determinística
    #     num_ctx=8192,           # Contexto enxuto economiza VRAM e acelera o prefill
    #     num_predict=1024,        # A resposta é apenas uma lista curta de nomes de tools
    #     reasoning=False,        # Desativa tokens de "pensamento" no Qwen 3 para resposta instantânea   
    # )
        
    # LLM = ChatOllama(
    #     model=MODEL,
    #     temperature=0.3,
    #     validate_model_on_init=True,
    #     num_ctx=16384,
    # )

    SUMARIZE_LLM = ChatGroq(
        model=SUMARIZE_MODEL,
        temperature=0,          # Essencial para seleção determinística
    )

    TOOL_SELECTION_LLM = ChatGroq(
        model=TOOL_SELECTION_MODEL,
        temperature=0,          # Essencial para seleção determinística,
    )

    LLM = ChatGroq(
        model=MODEL,
        temperature=0.3,
        reasoning_effort='medium'
    )

    MEMORY = InMemorySaver()

    state = SearchState()
    token = tavily_state.set(state)

    AGENT = create_agent(
        model=LLM,
        tools=tools,
        middleware=[ 
            SummarizationMiddleware(
                model=LLM,
                trigger=[
                    ("tokens", 12000),
                    ("messages", 10),
                ],
                keep=("messages", 6),
                summarizer=SUMARIZE_LLM,
                summary_prompt=SUMMARY_PROMPT
            ),
            LLMToolSelectorMiddleware(
                model=TOOL_SELECTION_LLM,
                max_tools=3,
                system_prompt=TOOL_SELECTION_PROMPT
            )
        ],
        checkpointer=MEMORY,
        system_prompt=SYSTEM_PROMPT,
    )

    return AGENT

    # STUDIO_AGENT = create_agent(
    #     model=LLM,
    #     tools=TOOLS,
    #     system_prompt=SYSTEM_PROMPT
    # )
