import os
import sys

# Add src directory to Python path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage

from langgraph.graph import StateGraph
from langgraph.graph import MessagesState, START, END

from utils.separator import separator

os.system("clear")


def mock_llm(state: MessagesState):
    return {"messages": AIMessage(content="Hello World!")}


graph = StateGraph(MessagesState)

graph.add_node(mock_llm)

graph.add_edge(START, "mock_llm")
graph.add_edge("mock_llm", END)

graph = graph.compile()

# ASCII IN TERMINAL
png_bytes = graph.get_graph().draw_ascii()
print(png_bytes)
print(separator(count=80))

messages: list[AnyMessage] = [HumanMessage(content="Hi!")]
res = graph.invoke({"messages": messages})

print(res)
