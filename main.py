from dotenv import load_dotenv

from langchain_core.messages import HumanMessage

from agents import personal_chief_agent

load_dotenv()

thread_config = { "configurable": {"thread_id": "1"} }

question = HumanMessage("I'm have only pasta, tomate paste and some bifs. What ")

response = personal_chief_agent.invoke({
    "messages": question,
}, config=thread_config)

print(response['messages'][-1].content)