from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent

from tools.web_search import web_search

SYSTEM_PROMPT = """
You're a restaurant chief that helps users makes easy food

Use web_search tool to up-to-date information and search for food with user ingrendient's
"""

MODEL = "gpt-oss:20b"

TOOLS = [web_search]

LLM = ChatOllama(
    model=MODEL,
    temperature=0.3,
    validate_model_on_init=True
)

MEMORY = InMemorySaver()

AGENT = create_agent(
    model=LLM,
    tools=TOOLS,
    checkpointer=MEMORY,
    system_prompt=SYSTEM_PROMPT
)

STUDIO_AGENT = create_agent(
    model=LLM,
    tools=TOOLS,
    system_prompt=SYSTEM_PROMPT
)