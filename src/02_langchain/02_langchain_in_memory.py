"""
This script demonstrates different types of conversation memory classes available in LangChain:

- ConversationBufferMemory: Stores the entire conversation history in memory.
  - now it is InMemoryChatMessageHistory
- ConversationBufferWindowMemory: Maintains a sliding window of recent messages.
  -
- ConversationTokenBufferMemory: Keeps conversation history up to a token limit.
- ConversationSummaryMemory: Summarizes conversation history to save memory and context.
"""

import os
import sys

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
from pydantic import SecretStr

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from enums.ai_models import OpenAIModels


load_dotenv()
os.system("clear")

# Safely load your API key from environment
api_key = os.getenv("REQUESTY_API_KEY")
if not api_key:
    raise ValueError("REQUESTY_API_KEY not found in environment variables.")
requesty_api_key: SecretStr = SecretStr(api_key)
llm: ChatOpenAI | None = None

# MEMORY IS MAINTAINED OUTSIDE THE CHAIN
store = {}  # memory is maintained outside the chain


def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]


##########################################################################
# INITIALIZE OPENAI CLIENT
##########################################################################
try:
    llm = ChatOpenAI(
        api_key=requesty_api_key,
        base_url="https://router.requesty.ai/v1",
        model=OpenAIModels.gpt5_nano,
        temperature=0,
    )

    # ✅ ASSERTION
    assert llm is not None, "Chat model not initialized"

    chain = RunnableWithMessageHistory(llm, get_session_history)

    # Example conversation with memory
    print("=== LangChain Memory Demo ===\n")

    # First message
    response1 = chain.invoke(
        "Hi I'm Bob. I like programming in Python.",
        config={"configurable": {"session_id": "1"}},
    )
    print("User: Hi I'm Bob. I like programming in Python.")
    print(f"Assistant: {response1.content}\n")

    # Second message - should remember Bob's name and interest
    response2 = chain.invoke(
        "What's my name and what do I like?",
        config={"configurable": {"session_id": "1"}},
    )
    print("User: What's my name and what do I like?")
    print(f"Assistant: {response2.content}\n")

    # Third message - different session (no memory)
    response3 = chain.invoke(
        "Do you remember my name?",
        config={"configurable": {"session_id": "2"}},
    )
    print("User (New Session): Do you remember my name?")
    print(f"Assistant: {response3.content}\n")

    # Fourth message - back to original session (memory restored)
    response4 = chain.invoke(
        "What programming language do I prefer?",
        config={"configurable": {"session_id": "1"}},
    )
    print("User (Original Session): What programming language do I prefer?")
    print(f"Assistant: {response4.content}\n")

    print("=== Memory Store Contents ===")
    for session_id, history in store.items():
        print(f"Session {session_id}: {len(history.messages)} messages")
        for i, msg in enumerate(history.messages):
            print(f"  {i + 1}. {msg.__class__.__name__}: {msg.content[:50]}...")

except Exception as e:
    llm = None
    print(e)
