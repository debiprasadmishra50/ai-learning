# LangChain ConversationBufferWindowMemory Migration Guide

## Overview

The `ConversationBufferWindowMemory` class has been deprecated in modern LangChain. This guide shows how to implement the same functionality using current LangChain patterns.

## Migration Summary

### Old Approach (Deprecated)

```python
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationChain

memory = ConversationBufferWindowMemory(k=5)  # Keep last 5 exchanges
chain = ConversationChain(llm=llm, memory=memory)
```

### New Approach (Current)

```python
from langchain_core.messages import trim_messages
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory

# Method 1: Custom WindowedChatMessageHistory
class WindowedChatMessageHistory(InMemoryChatMessageHistory):
    def __init__(self, max_messages: int = 10):
        super().__init__()
        self.max_messages = max_messages

    def add_message(self, message):
        super().add_message(message)
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

# Method 2: Using trim_messages
def get_trimmed_messages(messages, max_messages=10):
    return trim_messages(
        messages,
        max_tokens=max_messages,
        strategy="last",
        token_counter=lambda msgs: len(msgs)
    )
```

## Implementation Details

### 1. WindowedChatMessageHistory Class

The custom `WindowedChatMessageHistory` class extends `InMemoryChatMessageHistory` to automatically maintain a sliding window of messages:

```python
class WindowedChatMessageHistory(InMemoryChatMessageHistory):
    """Custom chat message history that maintains a sliding window of messages."""

    def __init__(self, max_messages: int = 10):
        super().__init__()
        self.max_messages = max_messages

    def add_message(self, message: BaseMessage) -> None:
        """Add a message and maintain the window size."""
        super().add_message(message)
        # Keep only the last max_messages
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
```

**Key Features:**

- Automatically trims old messages when limit is exceeded
- Maintains conversation flow by keeping recent context
- Configurable window size per session

### 2. trim_messages Function

The `trim_messages` function provides flexible message trimming:

```python
from langchain_core.messages import trim_messages

# Keep last 6 messages
trimmed = trim_messages(
    messages,
    max_tokens=6,
    strategy="last",
    token_counter=lambda msgs: len(msgs)
)

# Keep messages within token limit
trimmed = trim_messages(
    messages,
    max_tokens=1000,
    strategy="last",
    token_counter=lambda msgs: sum(len(msg.content) for msg in msgs)
)
```

**Parameters:**

- `max_tokens`: Maximum number of tokens/messages to keep
- `strategy`: "first" or "last" - which messages to keep
- `token_counter`: Function to count tokens (can count messages, characters, or actual tokens)
- `start_on`: "human" or "ai" - ensure trimmed conversation starts with specific message type

### 3. Integration with RunnableWithMessageHistory

```python
def get_windowed_session_history(session_id: str, max_messages: int = 6):
    """Create windowed memory with message limit."""
    key = f"{session_id}_{max_messages}"
    if key not in windowed_store:
        windowed_store[key] = WindowedChatMessageHistory(max_messages=max_messages)
    return windowed_store[key]

# Create chain with windowed memory
chain_windowed = RunnableWithMessageHistory(
    chain,
    lambda session_id: get_windowed_session_history(session_id, max_messages=4),
    input_messages_key="input",
    history_messages_key="history",
)
```

## Demonstration Program

The `src/02-langchain/03-langchain_context-memory.py` file demonstrates:

### 1. trim_messages Usage

- Shows how to trim conversation to specific message counts
- Demonstrates different trimming strategies
- Compares original vs trimmed conversations

### 2. Memory Comparison

- **Unlimited Memory**: Stores all conversation history
- **Windowed Memory**: Maintains only recent messages (configurable limit)
- Side-by-side comparison showing memory behavior

### 3. Different Window Sizes

- Tests window sizes of 2, 4, and 6 messages
- Shows how memory affects AI responses
- Demonstrates context retention vs memory efficiency

## Key Benefits

### Memory Efficiency

- **Reduced Memory Usage**: Only stores recent messages
- **Consistent Performance**: Memory usage doesn't grow indefinitely
- **Configurable Limits**: Adjust window size based on use case

### Context Management

- **Recent Context**: Maintains most relevant conversation history
- **Conversation Flow**: Preserves natural dialogue progression
- **Flexible Trimming**: Multiple strategies for message selection

### Session Management

- **Per-Session Windows**: Different limits for different conversations
- **Session Isolation**: Independent memory management
- **Dynamic Configuration**: Runtime adjustment of window sizes

## Best Practices

### 1. Choose Appropriate Window Size

```python
# For quick Q&A: 2-4 messages
window_size = 4

# For detailed conversations: 6-10 messages
window_size = 8

# For complex tasks: 10-20 messages
window_size = 15
```

### 2. Consider Message Types

```python
# Count human-AI pairs (recommended)
max_messages = 6  # 3 exchanges

# Count individual messages
max_messages = 10  # 5 exchanges
```

### 3. Token-Based Trimming

```python
# For token limits (more precise)
def count_tokens(messages):
    return sum(len(msg.content.split()) for msg in messages)

trimmed = trim_messages(
    messages,
    max_tokens=500,  # ~500 words
    token_counter=count_tokens
)
```

### 4. Preserve Important Messages

```python
# Always keep system message
def smart_trim(messages, max_messages=10):
    system_msgs = [msg for msg in messages if isinstance(msg, SystemMessage)]
    other_msgs = [msg for msg in messages if not isinstance(msg, SystemMessage)]

    # Trim other messages, keep system messages
    trimmed_others = trim_messages(other_msgs, max_tokens=max_messages-len(system_msgs))

    return system_msgs + trimmed_others
```

## Running the Demo

Execute the demonstration program:

```bash
python src/02-langchain/03-langchain_context-memory.py
```

This will show:

1. `trim_messages` function demonstration
2. Unlimited vs windowed memory comparison
3. Different window sizes behavior
4. Memory status tracking
5. Final memory state comparison

## Migration Checklist

- [ ] Replace `ConversationBufferWindowMemory` imports
- [ ] Implement `WindowedChatMessageHistory` or use `trim_messages`
- [ ] Update chain creation to use `RunnableWithMessageHistory`
- [ ] Configure appropriate window sizes for your use case
- [ ] Test memory behavior with your conversation patterns
- [ ] Update session management if needed
- [ ] Consider token-based limits for production use

This migration provides more flexibility and control over conversation memory while maintaining the core functionality of the deprecated `ConversationBufferWindowMemory`.
