"""
LangChain Memory Migration: Modern Replacements for Deprecated Memory Classes

This script demonstrates how to replace deprecated LangChain memory classes with modern approaches
using LangChain Expression Language (LCEL) and current best practices.

* Purpose: Shows advanced memory strategies that need custom control
* Use Case: When you need specific memory behaviors (limits, trimming, summarization)
* Approach: Manual memory management with trim_messages
* Memory Management: Manual - we control what gets stored and sent

DEPRECATED MEMORY CLASSES → MODERN REPLACEMENTS:

1. ConversationBufferMemory → InMemoryChatMessageHistory + RunnableWithMessageHistory
   - Stores entire conversation history in memory
   - Uses modern LCEL chain composition with `prompt | llm`

2. ConversationBufferWindowMemory → trim_messages with message counting
   - Maintains sliding window of recent messages (e.g., last 4 messages)
   - Uses `trim_messages()` with `token_counter=lambda msgs: len(msgs)`

3. ConversationTokenBufferMemory → trim_messages with token counting
   - Keeps conversation history up to a token limit (e.g., 100 tokens)
   - Uses `trim_messages()` with proper token counting function
   - Implements `count_message_tokens()` using `llm.get_num_tokens()`

4. ConversationSummaryMemory → Message summarization with recent message retention
   - Summarizes older messages while keeping recent ones detailed
   - Feeds summary as SystemMessage + recent messages to LLM
   - Automatically summarizes when message count exceeds limit

KEY CONCEPTS DEMONSTRATED:

- LangChain Expression Language (LCEL): `chain = prompt | llm`
- Modern chain composition with ChatPromptTemplate and MessagesPlaceholder
- trim_messages() function for memory management
- Token counting strategies for memory limits
- Message summarization for long conversations
- Interactive chatbot implementations with memory commands

USAGE:
Run the script to see interactive demos of each memory replacement pattern.
Each chatbot supports commands like 'quit', 'memory', and 'tokens' for testing.

MIGRATION REFERENCES:
- https://python.langchain.com/docs/versions/migrating_memory/
- https://langchain-ai.github.io/langgraph/how-tos/memory/add-memory/
"""

import os
import sys

from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
    trim_messages,
)
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
from pydantic import SecretStr

# Add src directory to Python path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from enums.ai_models import OpenAIModels
from utils.separator import separator

load_dotenv()
os.system("clear")

# Safely load your API key from environment
api_key = os.getenv("REQUESTY_API_KEY")
if not api_key:
    raise ValueError("REQUESTY_API_KEY not found in environment variables.")
requesty_api_key: SecretStr = SecretStr(api_key)
llm: ChatOpenAI | None = None

if not requesty_api_key:
    raise ValueError("REQUESTY_API_KEY not found in environment variables.")


# ==============================================================================
# SECTION: Demonstrate the trim_message
# ==============================================================================

print(separator(100))
print("LangChain Memory Migration: Modern Replacements for Deprecated Memory Classes")
print(separator(30))


def demonstrate_trim_messages():
    """Demonstrate trim_messages function for controlling context."""
    print("=== trim_messages Demo ===")

    # Create sample conversation
    messages = [
        HumanMessage("Hi, I'm Alice"),
        AIMessage("Hello Alice! Nice to meet you."),
        HumanMessage("I like programming"),
        AIMessage("That's great! What languages do you enjoy?"),
        HumanMessage("Python and JavaScript"),
        AIMessage("Excellent choices! Both are very versatile."),
        HumanMessage("Can you help me with a Python question?"),
        AIMessage("Of course! I'd be happy to help with Python."),
        HumanMessage("What's the difference between lists and tuples?"),
        AIMessage(
            "Lists are mutable (can be changed) while tuples are immutable (cannot be changed)."
        ),
    ]

    print(f"Original conversation: {len(messages)} messages")

    # Keep last 4 messages
    trimmed_4 = trim_messages(
        messages, max_tokens=4, strategy="last", token_counter=lambda msgs: len(msgs)
    )
    print(f"Trimmed to last 4: {len(trimmed_4)} messages")
    for msg in trimmed_4:
        print(f"  {msg.__class__.__name__}: {msg.content}")

    print()

    # Keep last 6 messages
    trimmed_6 = trim_messages(
        messages, max_tokens=6, strategy="last", token_counter=lambda msgs: len(msgs)
    )
    print(f"Trimmed to last 6: {len(trimmed_6)} messages")
    for msg in trimmed_6:
        print(f"  {msg.__class__.__name__}: {msg.content}")

    print("\n" + "=" * 50 + "\n")


# ==============================================================================
# SECTION: Simple Chatbot using trim_messages (Modern ConversationBufferWindowMemory)
# ==============================================================================


def simple_trim_messages_chatbot():
    """
    Simple chatbot demo using trim_messages as the modern replacement for ConversationBufferWindowMemory.
    This is the cleanest and most direct approach.
    """
    print(separator(60))
    print("=== Simple trim_messages Chatbot Demo ===")
    print("This demonstrates the modern replacement for ConversationBufferWindowMemory")
    print("Type 'quit' to exit, 'memory' to see current memory")
    print("-" * 60)

    # Initialize LLM
    try:
        llm = ChatOpenAI(
            api_key=requesty_api_key,
            base_url="https://router.requesty.ai/v1",
            model=OpenAIModels.gpt4o,
            temperature=0.0,
        )
    except Exception as e:
        print(f"Error initializing LLM: {e}")
        return

    # Create prompt template
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant. Keep responses concise and friendly.",
            ),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )

    # Create chain
    chain = prompt | llm

    # Store full conversation history
    conversation_history = []
    max_messages = 6  # Keep last 6 messages (3 exchanges)

    print(f"Chatbot initialized with window size: {max_messages} messages")

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() == "quit":
            print("Goodbye!")
            break
        elif user_input.lower() == "memory":
            # Show current memory using trim_messages
            trimmed = trim_messages(
                conversation_history,
                max_tokens=max_messages,
                strategy="last",
                token_counter=lambda msgs: len(msgs),
            )
            print(f"\nCurrent Memory ({len(trimmed)}/{max_messages} messages):")
            for i, msg in enumerate(trimmed, 1):
                msg_type = "Human" if isinstance(msg, HumanMessage) else "AI"
                print(f"  {i}. {msg_type}: {msg.content}")
            print(f"Total conversation: {len(conversation_history)} messages")
            continue
        elif not user_input:
            continue

        try:
            # Get trimmed history for context (this is the key part!)
            trimmed_history = trim_messages(
                conversation_history,
                max_tokens=max_messages,
                strategy="last",
                token_counter=lambda msgs: len(msgs),
            )

            # Get AI response with trimmed context
            response = chain.invoke({"input": user_input, "history": trimmed_history})

            # Add both messages to full history
            conversation_history.append(HumanMessage(content=user_input))
            conversation_history.append(AIMessage(content=response.content))

            print(f"Bot: {response.content}")

            # Show memory status
            current_trimmed = trim_messages(
                conversation_history,
                max_tokens=max_messages,
                strategy="last",
                token_counter=lambda msgs: len(msgs),
            )
            print(
                f"[Memory: {len(current_trimmed)}/{max_messages} messages, Total: {len(conversation_history)}]"
            )

        except Exception as e:
            print(f"Error: {e}")


# ==============================================================================
# SECTION: Demo with different window sizes
# Simple Chatbot using trim_messages (Modern ConversationBufferWindowMemory)
# ==============================================================================


def demo_different_window_sizes():
    """Demonstrate how different window sizes affect memory."""
    print("\n" + "=" * 60)
    print("=== Window Size Comparison Demo ===")

    try:
        llm = ChatOpenAI(
            api_key=requesty_api_key,
            base_url="https://router.requesty.ai/v1",
            model=OpenAIModels.gpt4o,
            temperature=0.0,
        )
    except Exception as e:
        print(f"Error initializing LLM: {e}")
        return

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )
    chain = prompt | llm

    # Test conversation
    test_messages = [
        "Hi, I'm Alice",
        "I love Python programming",
        "I work as a data scientist",
        "I enjoy hiking on weekends",
        "I have a cat named Whiskers",
        "What do you remember about me?",
    ]

    # Test different window sizes
    window_sizes = [2, 4, 6]

    for window_size in window_sizes:
        print(f"\n--- Testing Window Size: {window_size} messages ---")
        conversation = []

        for i, msg in enumerate(test_messages):
            # Get trimmed history
            trimmed_history = trim_messages(
                conversation,
                max_tokens=window_size,
                strategy="last",
                token_counter=lambda msgs: len(msgs),
            )

            # Get response
            response = chain.invoke({"input": msg, "history": trimmed_history})

            # Add to conversation
            conversation.append(HumanMessage(content=msg))
            conversation.append(AIMessage(content=response.content))

            print(f"Turn {i + 1}: {msg}")
            print(f"Bot: {response.content}")

            # Show what's in memory
            current_trimmed = trim_messages(
                conversation,
                max_tokens=window_size,
                strategy="last",
                token_counter=lambda msgs: len(msgs),
            )
            print(f"In Memory: {len(current_trimmed)}/{window_size} messages")

            if i == len(test_messages) - 1:  # Last message
                print(f"\nFinal Memory Contents:")
                for j, memory_msg in enumerate(current_trimmed, 1):
                    msg_type = "Human" if isinstance(memory_msg, HumanMessage) else "AI"
                    print(f"  {j}. {msg_type}: {memory_msg.content}")
            print()


# ==============================================================================
# SECTION: Token Buffer Memory (Modern ConversationTokenBufferMemory)
# ==============================================================================


def simple_token_buffer_chatbot():
    """
    Simple chatbot using trim_messages with token counting.
    Modern replacement for ConversationTokenBufferMemory.
    """
    print("\n" + "=" * 60)
    print("=== Token Buffer Chatbot Demo ===")
    print("Modern replacement for ConversationTokenBufferMemory")
    print("Type 'quit' to exit, 'memory' to see current memory")
    print("-" * 60)

    # Initialize LLM
    try:
        llm = ChatOpenAI(
            api_key=requesty_api_key,
            base_url="https://router.requesty.ai/v1",
            model=OpenAIModels.gpt4o,
            temperature=0.0,
        )
    except Exception as e:
        print(f"Error initializing LLM: {e}")
        return

    # Token counter function that works with trim_messages
    def count_message_tokens(messages):
        """Count tokens by summing all message content"""
        total_content = ""
        for msg in messages:
            total_content += msg.content
        return llm.get_num_tokens(total_content)

    # Create prompt template
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )

    # Create chain
    chain = prompt | llm

    # Store conversation history
    conversation_history = []
    MAX_TOKENS = 100  # Token limit

    print(f"Chatbot initialized with token limit: {MAX_TOKENS} tokens")

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() == "quit":
            print("Goodbye!")
            break
        elif user_input.lower() == "memory":
            # Show current memory
            trimmed = trim_messages(
                conversation_history,
                max_tokens=MAX_TOKENS,
                strategy="last",
                token_counter=count_message_tokens,
            )
            tokens_in_memory = count_message_tokens(trimmed)
            print(f"\nMemory ({tokens_in_memory}/{MAX_TOKENS} tokens):")
            for i, msg in enumerate(trimmed, 1):
                msg_type = "Human" if isinstance(msg, HumanMessage) else "AI"
                print(f"  {i}. {msg_type}: {msg.content}")
            continue
        elif not user_input:
            continue

        try:
            # Key part: Use trim_messages with proper token counting
            trimmed_history = trim_messages(
                conversation_history,
                max_tokens=MAX_TOKENS,
                strategy="last",
                token_counter=count_message_tokens,
            )

            # Get AI response
            response = chain.invoke({"input": user_input, "history": trimmed_history})

            # Add to history
            conversation_history.append(HumanMessage(content=user_input))
            conversation_history.append(AIMessage(content=response.content))

            print(f"Bot: {response.content}")

            # Show token status
            current_trimmed = trim_messages(
                conversation_history,
                max_tokens=MAX_TOKENS,
                strategy="last",
                token_counter=count_message_tokens,
            )

            tokens_used = count_message_tokens(current_trimmed)
            total_tokens = count_message_tokens(conversation_history)
            print(
                f"[Memory: {tokens_used}/{MAX_TOKENS} tokens, Total: {total_tokens} tokens]"
            )

        except Exception as e:
            print(f"Error: {e}")


# ==============================================================================
# SECTION: Summary Memory (Modern ConversationSummaryMemory)
# ==============================================================================


def simple_summary_memory_chatbot():
    """
    Simple chatbot using message summarization.
    Modern replacement for ConversationSummaryMemory.
    """
    print("\n" + "=" * 60)
    print("=== Summary Memory Chatbot Demo ===")
    print("Modern replacement for ConversationSummaryMemory")
    print("Type 'quit' to exit, 'memory' to see current memory")
    print("-" * 60)

    # Initialize LLM
    try:
        llm = ChatOpenAI(
            api_key=requesty_api_key,
            base_url="https://router.requesty.ai/v1",
            model=OpenAIModels.gpt4o,
            temperature=0.7,
        )
    except Exception as e:
        print(f"Error initializing LLM: {e}")
        return

    # Create prompt template
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )

    # Create chain
    chain = prompt | llm

    # Store conversation history
    conversation_history = []
    MAX_MESSAGES = 2  # Keep last 6 messages, summarize older ones
    SUMMARY = ""

    print(f"Chatbot initialized with message limit: {MAX_MESSAGES} messages")
    print("Older messages will be summarized to save memory")

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() == "quit":
            print("Goodbye!")
            break
        elif user_input.lower() == "memory":
            # Show current memory
            print("\nCurrent Memory:")
            if SUMMARY:
                print(f"Summary: {SUMMARY}")
            print(f"\nRecent messages ({len(conversation_history)}):")
            for i, msg in enumerate(conversation_history, 1):
                msg_type = "Human" if isinstance(msg, HumanMessage) else "AI"
                print(f"  {i}. {msg_type}: {msg.content}")
            continue
        elif user_input.lower() == "summary":
            print(f"\nCurrent Summary: {SUMMARY}")
            continue
        elif not user_input:
            continue

        try:
            # Prepare history for the LLM
            history_for_llm = []

            # Add summary as system message if it exists
            if SUMMARY:
                history_for_llm.append(
                    SystemMessage(content=f"Previous conversation summary: {SUMMARY}")
                )

            # Add recent messages
            history_for_llm.extend(conversation_history)

            # Get AI response
            response = chain.invoke({"input": user_input, "history": history_for_llm})

            # Add new messages to history
            conversation_history.append(HumanMessage(content=user_input))
            conversation_history.append(AIMessage(content=response.content))

            print(f"Bot: {response.content}")

            # Check if we need to summarize (keep only recent messages)
            if len(conversation_history) > MAX_MESSAGES:
                # Messages to summarize (older ones)
                messages_to_summarize = conversation_history[:-MAX_MESSAGES]

                # Create summary prompt
                summary_prompt = f"""
                Please provide a concise summary of this conversation:
                
                {chr(10).join([f"{type(msg).__name__}: {msg.content}" for msg in messages_to_summarize])}
                
                Summary:"""

                # Get summary
                summary_response = llm.invoke(summary_prompt)

                # Update summary (combine with existing if any)
                if SUMMARY:
                    SUMMARY = f"{SUMMARY} {summary_response.content}"
                else:
                    SUMMARY = summary_response.content

                # Keep only recent messages
                conversation_history = conversation_history[-MAX_MESSAGES:]

                print(f"[Summarized {len(messages_to_summarize)} older messages]")

        except Exception as e:
            print(f"Error: {e}")


# Run the demos
if __name__ == "__main__":
    # Demonstrate trim_messages first
    demonstrate_trim_messages()

    # Run the chatbot demo
    # simple_trim_messages_chatbot()

    # Run comparison demos
    # demo_different_window_sizes()

    # Run token buffer chatbot
    # simple_token_buffer_chatbot()

    # Run summary memory chatbot
    # simple_summary_memory_chatbot()
