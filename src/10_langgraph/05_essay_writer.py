import os
import sys
from pprint import pprint
from dotenv import load_dotenv

# Add src directory to Python path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI

from langchain_tavily import TavilySearch

from typing import TypedDict, List, cast
from pydantic import BaseModel, SecretStr

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
print("====== LANGGRAPH ESSAY WRITER EXAMPLE ======")
print(separator(count=80))

##########################################################################
# ✅ Setting TavilySearch Tool UP
##########################################################################
search_tool = TavilySearch(max_results=2)

##########################################################################
# ✅ Create MEMORY OR SQLITE Server Connection here
##########################################################################
memory_pointer = InMemorySaver()


##########################################################################
# ✅ Define the Agent State
##########################################################################
class AgentState(TypedDict):
    task: str
    plan: str
    draft: str
    critique: str
    content: List[str]
    revision_number: int
    max_revisions: int


##########################################################################
# ✅ Initialize OpenAI client
##########################################################################
model = ChatOpenAI(
    api_key=requesty_api_key,
    base_url="https://router.requesty.ai/v1",
    model=OpenAIModels.gpt5_nano,
    temperature=0,
)

##########################################################################
# ✅ WRITE THE PROMPTS
##########################################################################
PLAN_PROMPT = """You are an expert writer tasked with writing a high level outline of an essay. \
Write such an outline for the user provided topic. Give an outline of the essay along with any relevant notes \
or instructions for the sections."""

WRITER_PROMPT = """You are an essay assistant tasked with writing excellent 5-paragraph essays.\
Generate the best essay possible for the user's request and the initial outline. \
If the user provides critique, respond with a revised version of your previous attempts. \
Utilize all the information below as needed: 

------

{content}"""

REFLECTION_PROMPT = """You are a teacher grading an essay submission. \
Generate critique and recommendations for the user's submission. \
Provide detailed recommendations, including requests for length, depth, style, etc."""

RESEARCH_PLAN_PROMPT = """You are a researcher charged with providing information that can \
be used when writing the following essay. Generate a list of search queries that will gather \
any relevant information. Only generate 3 queries max."""

RESEARCH_CRITIQUE_PROMPT = """You are a researcher charged with providing information that can \
be used when making any requested revisions (as outlined below). \
Generate a list of search queries that will gather any relevant information. Only generate 3 queries max."""


##########################################################################
# ✅ Ensure we get a list of strings from Language Model, Define the scmena for it
##########################################################################
class Queries(BaseModel):
    queries: List[str]


##########################################################################
# ✅ Define the Agent and Nodes
##########################################################################
def plan_node(state: AgentState):
    messages = [
        SystemMessage(content=PLAN_PROMPT),
        HumanMessage(content=state["task"]),
    ]
    response = model.invoke(messages)
    return {"plan": response.content}


def research_plan_node(state: AgentState):
    messages = [
        SystemMessage(content=RESEARCH_PLAN_PROMPT),
        HumanMessage(content=state["plan"]),
    ]
    queries = cast(Queries, model.with_structured_output(Queries).invoke(messages))
    content = state["content"] or []
    for q in queries.queries:
        response = search_tool.invoke({"query": q})
        for r in response["results"]:
            content.append(r["content"])
    return {"content": content}


def generation_node(state: AgentState):
    content = "\n\n".join(state["content"] or [])
    user_message = HumanMessage(
        content=f"{state['task']}\n\nHere is tmy plan:\n\n{state['plan']}"
    )
    messages = [
        SystemMessage(content=WRITER_PROMPT.format(content=content)),
        user_message,
    ]

    response = model.invoke(messages)
    return {
        "draft": response.content,
        "revision_number": state.get("revision_number", 1) + 1,
    }


def reflection_node(state: AgentState):
    messages = [
        SystemMessage(content=REFLECTION_PROMPT),
        HumanMessage(content=state["draft"]),
    ]
    response = model.invoke(messages)
    return {"critique": response.content}


def research_critique_node(state: AgentState):
    messages = [
        SystemMessage(content=RESEARCH_CRITIQUE_PROMPT),
        HumanMessage(content=state["critique"]),
    ]
    queries = cast(Queries, model.with_structured_output(Queries).invoke(messages))
    content = state["content"] or []
    for q in queries.queries:
        response = search_tool.invoke({"query": q})
        for r in response["results"]:
            content.append(r["content"])
    return {"content": content}


def should_continue(state: AgentState):
    if state["revision_number"] > state["max_revisions"]:
        return END
    return "reflect"


##########################################################################
# ✅ Build the Graph Here
##########################################################################
graph = StateGraph(AgentState)

graph.add_node("planner", plan_node)
graph.add_node("generate", generation_node)
graph.add_node("reflect", reflection_node)
graph.add_node("research_plan", research_plan_node)
graph.add_node("research_critique", research_critique_node)

graph.set_entry_point("planner")
graph.add_conditional_edges(
    "generate", should_continue, {END: END, "reflect": "reflect"}
)

graph.add_edge("planner", "research_plan")
graph.add_edge("research_plan", "generate")
graph.add_edge("reflect", "research_critique")
graph.add_edge("research_critique", "generate")

graph = graph.compile(checkpointer=memory_pointer)


# ##########################################################################
# # ✅ Draw the Graph
# ##########################################################################
# graph = graph.get_graph()

# # ASCII IN TERMINAL
# png_bytes = graph.draw_ascii()
# print(png_bytes)
# print(separator(count=80))

# # MERMAID PNG
# graph.draw_mermaid_png(output_file_path=f"{os.path.dirname(__file__)}/essay-graph.png")

##########################################################################
# ✅ RUN THE GRAPH WITH STREAM
##########################################################################
thread: RunnableConfig = {"configurable": {"thread_id": "1"}}  # Top-level configurable
for s in graph.stream(
    {
        "task": "what is the difference between langchain and langgraph",
        "max_revisions": 2,
        "revision_number": 1,
        "plan": "",
        "draft": "",
        "critique": "",
        "content": [],
    },
    thread,
):
    for k, v in s.items():
        print("\n[+] EVENT:")
        print(f"KEY: {k}")
        pprint(v)
        print(separator(count=80))
