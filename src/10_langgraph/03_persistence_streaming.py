import os
import sys
from pprint import pprint
from dotenv import load_dotenv
import sqlite3

# Add src directory to Python path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.memory import InMemorySaver

from langchain_core.messages import HumanMessage, SystemMessage, AnyMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI

# from langchain_community.tools.tavily_search import TavilySearchResults # DEPRECATED
from langchain_tavily import TavilySearch  # NEW

from typing import TypedDict, Annotated
from pydantic import SecretStr
import operator

from utils.separator import separator
from enums.ai_models import OpenAIModels

load_dotenv()
os.system("clear")

# Safely load your API key from environment
api_key = os.getenv("REQUESTY_API_KEY")
if not api_key:
    raise ValueError("REQUESTY_API_KEY not found in environment variables.")
requesty_api_key: SecretStr = SecretStr(api_key)
chat: ChatOpenAI | None = None

print(separator(count=80))
print("====== LANGGRAPH PERSISTENCE & STREAMING EXAMPLES ======")
print(separator(count=80))

##########################################################################
# Setting TavilySearch Tool UP
##########################################################################
# search_tool = TavilySearchResults(max_results=2) # DEPRECATED
search_tool = TavilySearch(max_results=2)  # NEW
print(type(search_tool))
print(search_tool.name)
print(separator(count=80))


##########################################################################
# Create SQLITE Server Connection here
##########################################################################
memory_pointer = InMemorySaver()

# # File-based persistence (recommended)
# Creates DB file if missing
# conn = sqlite3.connect("langgraph.db", check_same_thread=False)
# conn.execute("SELECT 1")  # Initialize
# memory_pointer = SqliteSaver(conn)
# memory_pointer.setup()


##########################################################################
# ✅ Define the Agent State
##########################################################################
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]


##########################################################################
# Creating Agent Class, creating the graph, node and edges
##########################################################################
class Agent:
    def __init__(self, model, tools, checkpointer, system=""):  # Add Checkpointer
        self.system = system
        graph = StateGraph(AgentState)
        graph.add_node("llm", self.call_openai)
        graph.add_node("action", self.take_action)

        graph.add_conditional_edges(
            "llm", self.exists_action, {True: "action", False: END}
        )
        graph.add_edge("action", "llm")

        graph.set_entry_point("llm")

        # Compile with the checkpointer
        self.graph = graph.compile(checkpointer=checkpointer)

        self.tools = {t.name: t for t in tools}
        self.model = model.bind_tools(tools)

    def exists_action(self, state: AgentState):
        result = state["messages"][-1]
        return len(result.tool_calls) > 0  # type: ignore

    def call_openai(self, state: AgentState):
        messages = state["messages"]
        if self.system:
            messages = [SystemMessage(content=self.system)] + messages
        message = self.model.invoke(messages)
        return {"messages": [message]}

    def take_action(self, state: AgentState):
        tool_calls = state["messages"][-1].tool_calls  # type: ignore
        results = []
        for t in tool_calls:
            print(f"Calling: {t}")
            result = self.tools[t["name"]].invoke(t["args"])
            results.append(
                ToolMessage(tool_call_id=t["id"], name=t["name"], content=str(result))
            )
        print("Back to the model!")
        print(separator(count=80))
        return {"messages": results}


prompt = """You are a smart research assistant. Use the search engine to look up information. \
You are allowed to make multiple calls (either together or in sequence). \
Only look up information when you are sure of what you want. \
If you need to look up some information before asking a follow up question, you are allowed to do that!
"""

# Initialize OpenAI client
model = ChatOpenAI(
    api_key=requesty_api_key,
    base_url="https://router.requesty.ai/v1",
    model=OpenAIModels.gpt5_nano,
    temperature=0,
)

##########################################################################
# Inititlize the Agent
##########################################################################
# Pass the checkpointer
abot = Agent(model, [search_tool], memory_pointer, system=prompt)


##########################################################################
# Call the Agent
##########################################################################
messages: list[AnyMessage] = [HumanMessage(content="What is the weather in Delhi?")]
thread: RunnableConfig = {"configurable": {"thread_id": "1"}}  # Top-level configurable
for event in abot.graph.stream({"messages": messages}, thread):
    for v in event.values():
        print("EVENT:")
        pprint(v["messages"])
        print(separator(count=80))

print(separator(char="#", count=80))

messages = [HumanMessage(content="What about in la?")]
thread = {"configurable": {"thread_id": "1"}}
for event in abot.graph.stream({"messages": messages}, thread):
    for v in event.values():
        print("EVENT:")
        pprint(v["messages"])
        print(separator(count=80))

print(separator(char="#", count=80))

messages = [HumanMessage(content="Which one is warmer?")]
thread = {"configurable": {"thread_id": "1"}}
for event in abot.graph.stream({"messages": messages}, thread):
    for v in event.values():
        print("EVENT:")
        pprint(v["messages"])
        print(separator(count=80))

print(separator(char="#", count=80))


messages = [HumanMessage(content="Which one is warmer?")]
thread = {"configurable": {"thread_id": "2"}}
for event in abot.graph.stream({"messages": messages}, thread):
    for v in event.values():
        print("EVENT:")
        pprint(v["messages"])
        print(separator(count=80))


print(separator(count=80))

##########################################################################
# Draw the Graph
##########################################################################
graph = abot.graph.get_graph()

# ASCII IN TERMINAL
png_bytes = graph.draw_ascii()
print(png_bytes)
print(separator(count=80))

# MERMAID PNG
graph.draw_mermaid_png(output_file_path=f"{os.path.dirname(__file__)}/graph.png")
