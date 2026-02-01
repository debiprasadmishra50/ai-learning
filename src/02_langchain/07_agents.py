"""
LangChain: Agents (Updated for LangChain 1.2.7)

Outline:
* Using built-in LangChain tools: Wikipedia and Calculator
* Defining your own tools
* Creating agents with modern LangChain patterns
"""

import os
import sys
from dotenv import load_dotenv

# Add src directory to Python path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_core.globals import set_debug, set_verbose

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

from pydantic import SecretStr, BaseModel, Field
from datetime import date

from utils.separator import separator
from enums.ai_models import OpenAIModels

load_dotenv()
os.system("clear")

# Safely load your API key from environment
api_key = os.getenv("REQUESTY_API_KEY")
if not api_key:
    raise ValueError("[-] REQUESTY_API_KEY not found in environment variables.")
requesty_api_key: SecretStr = SecretStr(api_key)
llm: ChatOpenAI | None = None

try:
    # ✅ Initialize OpenAI client for chat-based LLM
    llm = ChatOpenAI(
        api_key=requesty_api_key,
        base_url="https://router.requesty.ai/v1",
        model=OpenAIModels.gpt5_nano,
        temperature=0,
    )
except Exception as e:
    print(f"[-] Warning: Could not initialize OpenAI client: {e}")
    llm = None

# ✅ ASSERTION
assert llm is not None, "Chat model not initialized"

print(separator(80))
print("[+] LANGCHAIN AGENTS - UPDATED FOR 1.2.7")
print(separator(80))

# ============================================================================
# EXAMPLE 1: SIMPLE CALCULATOR AGENT
# ============================================================================

print(separator(80))
print("[+] EXAMPLE 1: CALCULATOR TOOL")
print(separator(80))


@tool
def calculator(expression: str) -> str:
    """Useful for performing mathematical calculations.
    Input should be a valid mathematical expression as a string.
    Example: '0.25 * 300' to calculate 25% of 300"""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"


# Test the tool
print("[+] Testing calculator tool:")
print(f"[+] 25% of 300 = {calculator.invoke('0.25 * 300')}\n")

# Create agent with calculator
agent = create_agent(
    model=llm,
    tools=[calculator],
    system_prompt="You are a helpful assistant that can perform calculations.",
)

print("[+] Testing agent with math question:")
print("-" * 80)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "What is 25% of 300?"}]}
)

print(f"\n[+] Answer: {result['messages'][-1].content}\n")

# ============================================================================
# EXAMPLE 2: WIKIPEDIA AGENT
# ============================================================================

print(separator(80))
print("[+] EXAMPLE 2: WIKIPEDIA TOOL")
print(separator(80))

wikipedia = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=500)  # type: ignore
)

# Create agent with Wikipedia
wiki_agent = create_agent(
    model=llm,
    tools=[calculator, wikipedia],
    system_prompt="You are a helpful assistant with access to Wikipedia and calculator.",
)

question = "Tom M. Mitchell is an American computer scientist. What book did he write?"
print(f"Question: {question}")
print("-" * 80)

result = wiki_agent.invoke({"messages": [{"role": "user", "content": question}]})

print(f"\n[+] Answer: {result['messages'][-1].content}\n")

# ============================================================================
# EXAMPLE 3: CUSTOM DATE TOOL
# ============================================================================

print(separator(80))
print("[+] EXAMPLE 3: CUSTOM TOOL - DATE FUNCTION")
print(separator(80))


@tool
def get_today_date(query: str) -> str:
    """Returns today's date. Use this for any questions related to knowing today's date.
    The input can be any string, this function will always return today's date."""
    return str(date.today())


# Test the custom tool
print("[+] Testing custom date tool:")
print(f"[+] Today's date: {get_today_date.invoke('')}\n")

# Create agent with all tools
full_agent = create_agent(
    model=llm,
    tools=[calculator, wikipedia, get_today_date],
    system_prompt="You are a helpful assistant with access to various tools.",
)

print("[+] Testing agent with date question:")
print("-" * 80)

result = full_agent.invoke(
    {"messages": [{"role": "user", "content": "What's the date today?"}]}
)

print(f"\n[+] Answer: {result['messages'][-1].content}\n")

# ============================================================================
# EXAMPLE 4: STRUCTURED OUTPUT
# ============================================================================

print(separator(80))
print("[+] EXAMPLE 4: STRUCTURED OUTPUT")
print(separator(80))


class ContactInfo(BaseModel):
    """Contact information"""

    name: str = Field(description="Person's full name")
    email: str = Field(description="Email address")
    phone: str = Field(description="Phone number")


structured_agent = create_agent(model=llm, tools=[], response_format=ContactInfo)

print("Extracting structured contact info:")
print("-" * 80)

result = structured_agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Extract contact info: John Doe, john@example.com, (555) 123-4567",
            }
        ]
    }
)

contact = result.get("structured_response")
if contact:
    print("\n[+] Structured output:")
    print(f"[+]  Name: {contact.name}")
    print(f"[+]  Email: {contact.email}")
    print(f"[+]  Phone: {contact.phone}\n")

# ============================================================================
# EXAMPLE 5: STREAMING
# ============================================================================

print(separator(80))
print("[+] EXAMPLE 5: STREAMING AGENT RESPONSES")
print(separator(80))

print("[+] Streaming agent response:")
print("-" * 80)

for chunk in full_agent.stream(
    {"messages": [{"role": "user", "content": "What is 15% of 850?"}]},
    stream_mode="values",
):
    latest_message = chunk["messages"][-1]
    if hasattr(latest_message, "content") and latest_message.content:
        print(f"[+] Agent: {latest_message.content}")
    elif hasattr(latest_message, "tool_calls") and latest_message.tool_calls:
        tool_names = [tc["name"] for tc in latest_message.tool_calls]
        print(f"[+] Calling tools: {tool_names}")

print()

# ============================================================================
# EXAMPLE 6: PYTHON CODE EXECUTION (if you have langchain-experimental)
# ============================================================================

# print(separator(80))
# print("[+] EXAMPLE 6: PYTHON CODE EXECUTION (OPTIONAL)")
# print(separator(80))

# try:
#     from langchain_experimental.tools import PythonREPLTool

#     python_repl = PythonREPLTool()

#     python_agent = create_agent(
#         model=llm,
#         tools=[python_repl],
#         system_prompt="You are a Python coding assistant. Write and execute Python code to solve problems.",
#     )

#     customer_list = [
#         ["Harrison", "Chase"],
#         ["Lang", "Chain"],
#         ["Dolly", "Too"],
#     ]

#     print("[+] Task: Sort customers by last name")
#     print(f"[+] Input: {customer_list}")
#     print("-" * 80)

#     result = python_agent.invoke(
#         {
#             "messages": [
#                 {
#                     "role": "user",
#                     "content": f"Sort these customers by last name, then first name: {customer_list}",
#                 }
#             ]
#         }
#     )

#     print(f"\n[+] Answer: {result['messages'][-1].content}\n")
# except ImportError:
#     print("[-] ⚠️  langchain-experimental not installed. Skipping Python REPL example.")
#     print("[-] Install with: pip install langchain-experimental\n")

# ============================================================================
# SUMMARY
# ============================================================================

print("=" * 80)
print("SUMMARY - MODERN LANGCHAIN AGENTS (1.0+)")
print("=" * 80 + "\n")

print("""
✅ Key Points:

1. **Modern API**: Use create_agent() from langchain.agents
   - This uses LangGraph under the hood
   - Cleaner, more powerful API
   - Better streaming and state management

2. **Simple Invocation**:
   agent.invoke({"messages": [{"role": "user", "content": "..."}]})

3. **Tools**:
   - Define with @tool decorator
   - Can be functions or classes
   - Automatic schema generation

4. **Structured Output**:
   - Use response_format parameter
   - Works with Pydantic models
   - Automatic validation

5. **Streaming**:
   - Use agent.stream() for real-time updates
   - See intermediate tool calls
   - Better user experience

6. **No More**:
   - ❌ initialize_agent()
   - ❌ create_react_agent() + AgentExecutor()
   - ❌ load_tools()
   - ❌ AgentType enums

The new API is simpler and more powerful!
""")

print("=" * 80)
print("EXAMPLES COMPLETE")
print("=" * 80)
